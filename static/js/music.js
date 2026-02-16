document.addEventListener("DOMContentLoaded", function () {
    var trackRows = document.querySelectorAll(".track-row");
    if (!trackRows.length) return;

    // ── Configuration ──
    // "bars" = frequency equalizer, "oscilloscope" = waveform line
    var visualizerMode = "bars";

    // ── State ──
    var players = {};
    var trackOrder = [];
    var activeIndex = null;
    var audioContext = null;
    var analyser = null;
    var animationId = null;
    var isExpanded = false;

    // ── Now Playing DOM refs ──
    var npCard = document.getElementById("now-playing");
    var npIdle = document.getElementById("np-idle");
    var npActive = document.getElementById("np-active");
    var npTitle = document.getElementById("np-title");
    var npCurrentTime = document.getElementById("np-current-time");
    var npDuration = document.getElementById("np-duration");
    var npPlayPause = document.getElementById("np-play-pause");
    var npPlayIcon = document.getElementById("np-play-icon");
    var npPauseIcon = document.getElementById("np-pause-icon");
    var npPrev = document.getElementById("np-prev");
    var npNext = document.getElementById("np-next");
    var canvas = document.getElementById("visualizer-canvas");
    var ctx = canvas ? canvas.getContext("2d") : null;

    // ── Helpers ──
    function getColors() {
        var isDark = document.documentElement.classList.contains("dark");
        return {
            waveColor: isDark ? "#404040" : "#d4d4d4",
            progressColor: isDark ? "#22c55e" : "#16a34a",
            barColor: isDark ? "#22c55e" : "#16a34a",
        };
    }

    function parseDuration(row) {
        var text = row.querySelector(".track-duration").textContent.trim();
        var parts = text.split(":");
        return parseInt(parts[0]) * 60 + parseInt(parts[1]);
    }

    function formatTime(seconds) {
        var s = Math.floor(seconds);
        var m = Math.floor(s / 60);
        s = s % 60;
        return m + ":" + (s < 10 ? "0" : "") + s;
    }

    function setPlayState(index, playing) {
        var player = players[index];
        if (!player) return;
        var playIcon = player.row.querySelector(".play-icon");
        var pauseIcon = player.row.querySelector(".pause-icon");
        playIcon.classList.toggle("hidden", playing);
        pauseIcon.classList.toggle("hidden", !playing);
    }

    function setNpPlayState(playing) {
        npPlayIcon.classList.toggle("hidden", playing);
        npPauseIcon.classList.toggle("hidden", !playing);
    }

    function highlightActiveRow(index) {
        trackRows.forEach(function (row) {
            row.classList.remove("bg-green-50", "dark:bg-green-950/30");
        });
        if (index !== null && players[index]) {
            players[index].row.classList.add("bg-green-50", "dark:bg-green-950/30");
        }
    }

    // ── Audio Context + Analyser ──
    function ensureAudioContext() {
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 1024;
            analyser.smoothingTimeConstant = 0.6;
            analyser.minDecibels = -85;
            analyser.maxDecibels = -10;
            analyser.connect(audioContext.destination);
        }
        if (audioContext.state === "suspended") {
            audioContext.resume();
        }
    }

    function connectAudio(index) {
        var player = players[index];
        if (!player || player.sourceConnected) return;
        ensureAudioContext();
        var mediaEl = player.ws.getMediaElement();
        if (mediaEl) {
            var source = audioContext.createMediaElementSource(mediaEl);
            source.connect(analyser);
            player.sourceConnected = true;
        }
    }

    // ── Visualizer ──
    function resizeCanvas() {
        if (!canvas) return;
        var rect = canvas.parentElement.getBoundingClientRect();
        canvas.width = Math.floor(rect.width);
    }

    // ── Frequency Bars ──
    var NUM_BARS = 48;

    function buildLogBins(bufferLength, numBars) {
        var minBin = 2;
        // Cap at ~16kHz (bin 370 at 44.1kHz with fftSize 1024) so top bars have audible energy
        var maxBin = Math.min(bufferLength, Math.floor(bufferLength * 0.72));
        var logMin = Math.log(minBin);
        var logMax = Math.log(maxBin);
        var rawBins = [];
        for (var i = 0; i < numBars; i++) {
            var startLog = logMin + (logMax - logMin) * (i / numBars);
            var endLog = logMin + (logMax - logMin) * ((i + 1) / numBars);
            var start = Math.floor(Math.exp(startLog));
            var end = Math.max(start + 1, Math.floor(Math.exp(endLog)));
            rawBins.push({
                start: Math.min(start, maxBin - 1),
                end: Math.min(end, maxBin),
            });
        }
        // Deduplicate: collapse bars that map to the same FFT range
        var bins = [rawBins[0]];
        for (var i = 1; i < rawBins.length; i++) {
            var prev = bins[bins.length - 1];
            if (rawBins[i].start !== prev.start || rawBins[i].end !== prev.end) {
                bins.push(rawBins[i]);
            }
        }
        return bins;
    }

    function drawBars() {
        if (!ctx || !analyser) return;

        var bufferLength = analyser.frequencyBinCount;
        var dataArray = new Uint8Array(bufferLength);
        analyser.getByteFrequencyData(dataArray);

        var width = canvas.width;
        var height = canvas.height;
        var colors = getColors();

        ctx.clearRect(0, 0, width, height);

        var logBins = buildLogBins(bufferLength, NUM_BARS);
        var numBars = logBins.length;
        var gap = 2;
        var barWidth = Math.max(3, Math.floor((width - gap * (numBars - 1)) / numBars));
        var totalBarWidth = barWidth + gap;
        var offsetX = Math.floor((width - numBars * totalBarWidth + gap) / 2);

        for (var i = 0; i < numBars; i++) {
            var sum = 0;
            var count = 0;
            for (var j = logBins[i].start; j < logBins[i].end; j++) {
                sum += dataArray[j];
                count++;
            }
            var avg = count > 0 ? sum / count : 0;

            // Tilt: quadratic curve so mids stay flat, only highs get boosted
            var t = i / numBars;
            var tilt = 1.0 + t * t * 2.2;
            var normalized = Math.min(avg * tilt / 255, 1.0);
            var scaled = Math.pow(normalized, 1.8);
            var barHeight = Math.max(2, scaled * height);
            var x = offsetX + i * totalBarWidth;
            var y = height - barHeight;

            ctx.fillStyle = colors.barColor;
            ctx.beginPath();
            var radius = Math.min(barWidth / 2, 3);
            ctx.roundRect(x, y, barWidth, barHeight, [radius, radius, 0, 0]);
            ctx.fill();
        }
    }

    // ── Oscilloscope Waveform ──
    var OSC_POINTS = 128;
    var oscSmoothed = null;
    var OSC_LERP = 0.35;

    function drawOscilloscope() {
        if (!ctx || !analyser) return;

        var bufferLength = analyser.fftSize;
        var dataArray = new Uint8Array(bufferLength);
        analyser.getByteTimeDomainData(dataArray);

        // Downsample to OSC_POINTS
        var step = Math.floor(bufferLength / OSC_POINTS);
        if (!oscSmoothed) {
            oscSmoothed = new Float32Array(OSC_POINTS);
            for (var i = 0; i < OSC_POINTS; i++) {
                oscSmoothed[i] = 0.5;
            }
        }

        // Lerp toward new values for smooth motion
        for (var i = 0; i < OSC_POINTS; i++) {
            var target = dataArray[i * step] / 255.0;
            oscSmoothed[i] += (target - oscSmoothed[i]) * OSC_LERP;
        }

        var width = canvas.width;
        var height = canvas.height;
        var colors = getColors();

        ctx.clearRect(0, 0, width, height);

        ctx.lineWidth = 2;
        ctx.strokeStyle = colors.barColor;
        ctx.beginPath();

        var sliceWidth = width / (OSC_POINTS - 1);
        for (var i = 0; i < OSC_POINTS; i++) {
            var x = i * sliceWidth;
            var y = oscSmoothed[i] * height;

            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                // Smooth curve through points
                var prevX = (i - 1) * sliceWidth;
                var cpX = (prevX + x) / 2;
                ctx.quadraticCurveTo(prevX, oscSmoothed[i - 1] * height, cpX, (oscSmoothed[i - 1] * height + y) / 2);
            }
        }
        ctx.lineTo(width, oscSmoothed[OSC_POINTS - 1] * height);
        ctx.stroke();
    }

    // ── Visualization loop ──
    function drawFrame() {
        if (visualizerMode === "oscilloscope") {
            drawOscilloscope();
        } else {
            drawBars();
        }
        animationId = requestAnimationFrame(drawFrame);
    }

    function startVisualization() {
        if (animationId) return;
        resizeCanvas();
        animationId = requestAnimationFrame(drawFrame);
    }

    function stopVisualization() {
        if (animationId) {
            cancelAnimationFrame(animationId);
            animationId = null;
        }
    }

    function clearCanvas() {
        stopVisualization();
        if (ctx && canvas) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    }

    // ── Now Playing UI ──
    function expandNowPlaying(index) {
        var player = players[index];
        if (!player) return;
        if (!isExpanded) {
            npIdle.classList.add("hidden");
            npActive.classList.remove("hidden");
            isExpanded = true;
        }
        npTitle.textContent = player.row.querySelector(".track-title").textContent;
        npDuration.textContent = player.row.querySelector(".track-duration").textContent;
        npCurrentTime.textContent = "0:00";
    }

    function updateNpTime(currentTime) {
        npCurrentTime.textContent = formatTime(currentTime);
    }

    // ── Playlist ──
    function getPlaylistPosition(index) {
        return trackOrder.indexOf(index);
    }

    function playTrack(index) {
        if (activeIndex !== null && activeIndex !== index && players[activeIndex]) {
            players[activeIndex].ws.pause();
            setPlayState(activeIndex, false);
        }

        var player = players[index];
        if (!player) return;

        connectAudio(index);
        expandNowPlaying(index);
        highlightActiveRow(index);
        player.ws.play();
        setPlayState(index, true);
        setNpPlayState(true);
        activeIndex = index;
        startVisualization();
    }

    function pauseTrack() {
        if (activeIndex === null || !players[activeIndex]) return;
        players[activeIndex].ws.pause();
        setPlayState(activeIndex, false);
        setNpPlayState(false);
        stopVisualization();
    }

    function playNext() {
        if (activeIndex === null) return;
        var pos = getPlaylistPosition(activeIndex);
        if (pos < trackOrder.length - 1) {
            playTrack(trackOrder[pos + 1]);
        } else {
            pauseTrack();
            clearCanvas();
        }
    }

    function playPrev() {
        if (activeIndex === null) return;
        var player = players[activeIndex];
        if (player && player.ws.getCurrentTime() > 3) {
            player.ws.seekTo(0);
            return;
        }
        var pos = getPlaylistPosition(activeIndex);
        if (pos > 0) {
            playTrack(trackOrder[pos - 1]);
        } else {
            if (player) player.ws.seekTo(0);
        }
    }

    // ── Init wavesurfer instances ──
    trackRows.forEach(function (row) {
        var index = row.dataset.trackIndex;
        var peaksUrl = row.dataset.peaksUrl;
        var audioUrl = row.dataset.audioUrl;
        var container = row.querySelector(".track-waveform");
        var duration = parseDuration(row);

        trackOrder.push(index);

        fetch(peaksUrl)
            .then(function (res) { return res.json(); })
            .then(function (peakData) {
                var colors = getColors();
                var ws = WaveSurfer.create({
                    container: container,
                    height: 40,
                    barWidth: 2,
                    barGap: 1,
                    barRadius: 2,
                    waveColor: colors.waveColor,
                    progressColor: colors.progressColor,
                    cursorColor: "transparent",
                    backend: "MediaElement",
                    peaks: peakData.data,
                    duration: duration,
                    interact: true,
                    normalize: true,
                    url: audioUrl,
                    media: document.createElement("audio"),
                });

                players[index] = { ws: ws, row: row, sourceConnected: false };

                ws.on("finish", function () {
                    setPlayState(index, false);
                    playNext();
                });

                ws.on("timeupdate", function (currentTime) {
                    if (activeIndex === index) {
                        updateNpTime(currentTime);
                    }
                });
            })
            .catch(function () {
                // Peak file missing or failed to load
            });
    });

    // ── Tracklist click handler ──
    document.addEventListener("click", function (e) {
        var btn = e.target.closest(".track-play-btn");
        if (!btn) return;
        var row = btn.closest(".track-row");
        if (!row) return;
        var index = row.dataset.trackIndex;
        var player = players[index];
        if (!player) return;

        if (activeIndex === index && player.ws.isPlaying()) {
            pauseTrack();
        } else {
            playTrack(index);
        }
    });

    // ── Now Playing controls ──
    if (npPlayPause) {
        npPlayPause.addEventListener("click", function () {
            if (activeIndex === null) return;
            var player = players[activeIndex];
            if (!player) return;
            if (player.ws.isPlaying()) {
                pauseTrack();
            } else {
                player.ws.play();
                setPlayState(activeIndex, true);
                setNpPlayState(true);
                startVisualization();
            }
        });
    }

    if (npNext) {
        npNext.addEventListener("click", function () {
            if (activeIndex === null) return;
            var pos = getPlaylistPosition(activeIndex);
            if (pos < trackOrder.length - 1) {
                playTrack(trackOrder[pos + 1]);
            }
        });
    }

    if (npPrev) {
        npPrev.addEventListener("click", function () {
            playPrev();
        });
    }

    // ── Visualizer mode toggle ──
    var vizToggle = document.getElementById("np-viz-toggle");
    var vizIconBars = document.getElementById("viz-icon-bars");
    var vizIconOsc = document.getElementById("viz-icon-osc");
    if (vizToggle) {
        vizToggle.addEventListener("click", function () {
            if (visualizerMode === "bars") {
                visualizerMode = "oscilloscope";
                vizIconBars.classList.add("hidden");
                vizIconOsc.classList.remove("hidden");
            } else {
                visualizerMode = "bars";
                vizIconOsc.classList.add("hidden");
                vizIconBars.classList.remove("hidden");
            }
        });
    }

    // ── Visibility change: pause/resume to prevent speed-up on mobile ──
    var wasPlayingBeforeHide = false;
    document.addEventListener("visibilitychange", function () {
        if (document.hidden) {
            if (activeIndex !== null && players[activeIndex] && players[activeIndex].ws.isPlaying()) {
                wasPlayingBeforeHide = true;
                pauseTrack();
            } else {
                wasPlayingBeforeHide = false;
            }
        } else {
            if (wasPlayingBeforeHide && activeIndex !== null && players[activeIndex]) {
                wasPlayingBeforeHide = false;
                playTrack(activeIndex);
            }
        }
    });

    // ── Canvas resize ──
    window.addEventListener("resize", function () {
        if (animationId) {
            resizeCanvas();
        }
    });

    // ── Theme sync ──
    var themeToggle = document.getElementById("theme-toggle");
    if (themeToggle) {
        themeToggle.addEventListener("click", function () {
            setTimeout(function () {
                var colors = getColors();
                Object.keys(players).forEach(function (key) {
                    players[key].ws.setOptions({
                        waveColor: colors.waveColor,
                        progressColor: colors.progressColor,
                    });
                });
            }, 50);
        });
    }
});
