document.addEventListener('DOMContentLoaded', () => {
    // Sections
    const uploadArea = document.getElementById('uploadArea');
    const configArea = document.getElementById('configArea');
    const loadingArea = document.getElementById('loadingArea');
    const resultArea = document.getElementById('resultArea');

    // Inputs/Buttons
    const fileInput = document.getElementById('fileInput');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const processBtn = document.getElementById('processBtn');
    const startOverBtn = document.getElementById('startOverBtn');

    // Elements
    const fileNameDisplay = document.getElementById('fileName');
    const originalAudio = document.getElementById('originalAudio');
    const processedAudio = document.getElementById('processedAudio');
    const errorBanner = document.getElementById('errorBanner');

    // Settings
    const thresholdSlider = document.getElementById('thresholdSlider');
    const durationSlider = document.getElementById('durationSlider');
    const thresholdVal = document.getElementById('thresholdVal');
    const durationVal = document.getElementById('durationVal');

    // Stats
    const statOriginal = document.getElementById('statOriginal');
    const statRemoved = document.getElementById('statRemoved');
    const statNew = document.getElementById('statNew');
    const downloadLink = document.getElementById('downloadLink');

    let currentFile = null;

    // ----- UI Interactions ----- //

    // Sliders
    thresholdSlider.addEventListener('input', (e) => {
        thresholdVal.textContent = `${e.target.value} dB`;
    });

    durationSlider.addEventListener('input', (e) => {
        durationVal.textContent = `${e.target.value} s`;
    });

    // Drag & Drop
    uploadArea.addEventListener('click', () => fileInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    removeFileBtn.addEventListener('click', () => {
        resetApp();
    });

    startOverBtn.addEventListener('click', () => {
        resetApp();
    });

    // ----- Logic ----- //

    function handleFileSelect(file) {
        hiddenError();
        const validExtensions = ['mp3', 'wav', 'm4a', 'flac', 'ogg'];
        const ext = file.name.split('.').pop().toLowerCase();

        if (!validExtensions.includes(ext)) {
            showError("Invalid file type. Supported: MP3, WAV, M4A, FLAC, OGG.");
            return;
        }

        currentFile = file;
        fileNameDisplay.textContent = file.name;

        // Setup original audio preview
        const fileURL = URL.createObjectURL(file);
        originalAudio.src = fileURL;

        // Switch section
        uploadArea.style.display = 'none';
        configArea.style.display = 'block';
    }

    processBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        hiddenError();
        configArea.style.display = 'none';
        loadingArea.style.display = 'block';

        const formData = new FormData();
        formData.append('audio', currentFile);
        formData.append('threshold', thresholdSlider.value);
        formData.append('duration', durationSlider.value);

        try {
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                showResults(data);
            } else {
                throw new Error(data.error || 'Failed to process audio');
            }
        } catch (err) {
            loadingArea.style.display = 'none';
            configArea.style.display = 'block';
            showError(err.message);
        }
    });

    function showResults(data) {
        loadingArea.style.display = 'none';
        resultArea.style.display = 'block';

        statOriginal.textContent = `${data.original_duration.toFixed(2)}s`;
        statRemoved.textContent = `${data.silence_removed.toFixed(2)}s`;
        statNew.textContent = `${data.new_duration.toFixed(2)}s`;

        processedAudio.src = data.download_url;
        downloadLink.href = data.download_url;
        downloadLink.download = currentFile.name.replace(/(\.[\w\d_-]+)$/i, '_processed$1');

        // Reset file input so same file can be uploaded again if needed
        fileInput.value = '';
    }

    function resetApp() {
        currentFile = null;
        fileInput.value = '';
        originalAudio.pause();
        originalAudio.src = '';
        processedAudio.pause();
        processedAudio.src = '';
        hiddenError();

        configArea.style.display = 'none';
        resultArea.style.display = 'none';
        loadingArea.style.display = 'none';
        uploadArea.style.display = 'block';
    }

    function showError(msg) {
        errorBanner.textContent = msg;
        errorBanner.style.display = 'block';
    }

    function hiddenError() {
        errorBanner.style.display = 'none';
        errorBanner.textContent = '';
    }
});
