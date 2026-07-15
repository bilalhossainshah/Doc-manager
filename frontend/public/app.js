document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://localhost:8000'; // FastAPI backend

    // Elements
    const userIdInput = document.getElementById('user_id');
    const fileInput = document.getElementById('file');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const uploadForm = document.getElementById('uploadForm');
    const uploadStatus = document.getElementById('uploadStatus');
    const queryForm = document.getElementById('queryForm');
    const questionInput = document.getElementById('question');
    const chatContainer = document.getElementById('chatContainer');

    // File input change listener to update display name
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileNameDisplay.textContent = e.target.files[0].name;
            fileNameDisplay.classList.add('text-blue-400');
        } else {
            fileNameDisplay.textContent = 'Drag and drop or click to browse';
            fileNameDisplay.classList.remove('text-blue-400');
        }
    });

    // Handle File Upload
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const userId = userIdInput.value.trim();
        const file = fileInput.files[0];

        if (!userId) {
            showUploadStatus('Please enter a User ID.', 'text-red-400');
            return;
        }

        if (!file) {
            showUploadStatus('Please select a file to upload.', 'text-red-400');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        showUploadStatus('<i class="fas fa-spinner fa-spin mr-2"></i> Uploading and processing...', 'text-blue-400');

        try {
            const response = await fetch(`${API_BASE_URL}/upload?user_id=${encodeURIComponent(userId)}`, {
                method: 'POST',
                body: formData,
                // Note: Don't set Content-Type header when using FormData,
                // the browser will automatically set it with the correct boundary.
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `Server error: ${response.status}`);
            }

            const data = await response.json();
            showUploadStatus(`<i class="fas fa-check-circle mr-2"></i> ${data.message || 'Success!'}`, 'text-green-400');

            // Reset form
            fileInput.value = '';
            fileNameDisplay.textContent = 'Drag and drop or click to browse';
            fileNameDisplay.classList.remove('text-blue-400');

        } catch (error) {
            console.error('Upload Error:', error);
            showUploadStatus(`<i class="fas fa-exclamation-circle mr-2"></i> ${error.message}`, 'text-red-400');
        }
    });

    function showUploadStatus(html, colorClass) {
        uploadStatus.innerHTML = html;
        uploadStatus.className = `mt-4 text-sm text-center block ${colorClass}`;
    }

    // Handle Query
    queryForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const userId = userIdInput.value.trim();
        const question = questionInput.value.trim();

        if (!userId) {
            alert('Please enter a User ID.');
            return;
        }

        if (!question) return;

        // Clear default message if it's the first chat
        if (chatContainer.children.length === 1 && chatContainer.children[0].classList.contains('text-center')) {
            chatContainer.innerHTML = '';
        }

        // Add User Message
        appendMessage(question, 'user');
        questionInput.value = '';

        // Add Loading indicator
        const loadingId = appendMessage('<i class="fas fa-ellipsis-h fa-fade"></i>', 'bot', true);

        try {
            const response = await fetch(`${API_BASE_URL}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId,
                    question: question
                }),
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `Server error: ${response.status}`);
            }

            const data = await response.json();

            // Remove loading
            document.getElementById(loadingId)?.remove();

            // The backend returns { "answer": "..." } or similar based on retrieval.py
            // Let's assume it returns a string if it's direct, or data.answer, or data.result
            const botReply = data.answer || data.result || typeof data === 'string' ? data : JSON.stringify(data);

            appendMessage(botReply, 'bot');

        } catch (error) {
            console.error('Query Error:', error);
            document.getElementById(loadingId)?.remove();
            appendMessage(`Error: ${error.message}`, 'error');
        }
    });

    function appendMessage(text, sender, isLoading = false) {
        const id = 'msg-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.id = id;
        msgDiv.className = `max-w-[80%] rounded-2xl px-4 py-2 mb-3 text-sm ${
            sender === 'user'
                ? 'bg-blue-600 text-white self-end ml-auto rounded-tr-sm'
                : sender === 'error'
                    ? 'bg-red-500/20 text-red-200 border border-red-500/50 self-start mr-auto rounded-tl-sm'
                    : 'bg-slate-700 text-slate-200 self-start mr-auto rounded-tl-sm'
        }`;

        msgDiv.innerHTML = text;
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        return id;
    }
});