/**
 * XChange Common & Specific JavaScript
 */

// Theme Management
function initTheme() {
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
}

function toggleTheme() {
    document.documentElement.classList.toggle('dark');
    localStorage.theme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
}

// Notifications
function showNotification(message, type = 'info') {
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'fixed bottom-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    const bgColor = type === 'error' ? 'bg-red-500' : 'bg-green-600';
    toast.className = `${bgColor} text-white px-6 py-3 rounded-lg shadow-xl transform transition-all duration-300 translate-y-10 opacity-0 pointer-events-auto min-w-[200px] text-center font-medium`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-y-10', 'opacity-0');
    }, 10);
    
    // Auto-remove
    setTimeout(() => {
        toast.classList.add('translate-y-10', 'opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Global Config
window.appConfig = null;

async function loadConfig() {
    try {
        const res = await fetch('/config');
        const config = await res.json();
        window.appConfig = config;
        return config;
    } catch (e) {
        console.error('Failed to load config', e);
        return null;
    }
}

// Creation Logic
function setupCreateForm() {
    const typeSelect = document.getElementById('type');
    const contentInput = document.getElementById('content-input');
    const fileInput = document.getElementById('file-input');
    const fastForwardContainer = document.getElementById('fast-forward-container');
    const syntaxContainer = document.getElementById('syntax-container');
    const dropZone = document.getElementById('drop-zone');
    const fileInputEl = document.getElementById('file');
    const dropText = document.getElementById('drop-text');
    const syntaxSelect = document.getElementById('syntax');
    const contentTextArea = document.getElementById('content');
    const previewArea = document.getElementById('create-preview');
    const previewCode = document.getElementById('create-preview-code');

    const onTypeChange = () => {
        const linkInput = document.getElementById('link-content');
        
        // Reset inputs
        contentTextArea.value = '';
        linkInput.value = '';
        fileInputEl.value = '';
        dropText.textContent = 'Drag & Drop file here, or click to select';
        document.getElementById('image-preview').classList.add('hidden');
        updatePreview(); // Clear preview

        if (typeSelect.value === 'file') {
            contentInput.classList.add('hidden');
            fileInput.classList.remove('hidden');
            fastForwardContainer.classList.add('hidden');
            syntaxContainer.classList.add('hidden');
        } else {
            contentInput.classList.remove('hidden');
            fileInput.classList.add('hidden');
            if (typeSelect.value === 'link') {
                fastForwardContainer.classList.remove('hidden');
                syntaxContainer.classList.add('hidden');
                contentTextArea.classList.add('hidden');
                contentTextArea.disabled = true;
                linkInput.classList.remove('hidden');
                linkInput.disabled = false;
            } else {
                fastForwardContainer.classList.add('hidden');
                syntaxContainer.classList.remove('hidden');
                contentTextArea.classList.remove('hidden');
                contentTextArea.disabled = false;
                linkInput.classList.add('hidden');
                linkInput.disabled = true;
            }
        }
    };

    function updatePreview() {
        if (typeSelect.value === 'text' && contentTextArea.value.trim() !== '') {
            previewArea.classList.remove('hidden');
            previewCode.textContent = contentTextArea.value;
            previewCode.className = 'language-' + (syntaxSelect.value || 'plain');
            if (window.Prism) {
                Prism.highlightElement(previewCode);
            }
        } else {
            previewArea.classList.add('hidden');
        }
    }

    typeSelect.onchange = onTypeChange;
    syntaxSelect.onchange = updatePreview;
    contentTextArea.oninput = updatePreview;

    // Drag & Drop
    dropZone.onclick = () => fileInputEl.click();
    dropZone.ondragover = (e) => {
        e.preventDefault();
        dropZone.classList.add('border-blue-500', 'bg-blue-50', 'dark:bg-blue-900/20');
    };
    dropZone.ondragleave = () => dropZone.classList.remove('border-blue-500', 'bg-blue-50', 'dark:bg-blue-900/20');
    dropZone.ondrop = (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-blue-500', 'bg-blue-50', 'dark:bg-blue-900/20');
        if (e.dataTransfer.files.length) {
            fileInputEl.files = e.dataTransfer.files;
            handleFileSelect(fileInputEl);
        }
    };

    fileInputEl.onchange = () => handleFileSelect(fileInputEl);

    function handleFileSelect(input) {
        const file = input.files[0];
        if (!file) return;

        if (window.appConfig && window.appConfig.MAX_FILE_SIZE && file.size > window.appConfig.MAX_FILE_SIZE) {
            showNotification(`File too large! Max size is ${Math.round(window.appConfig.MAX_FILE_SIZE / 1024 / 1024)}MB`, 'error');
            input.value = '';
            dropText.textContent = 'Drag & Drop file here, or click to select';
            return;
        }

        dropText.textContent = `Selected: ${file.name}`;
        previewImage(input);
    }

    function previewImage(input) {
        const preview = document.getElementById('image-preview');
        const img = document.getElementById('preview-img');
        if (input.files && input.files[0] && input.files[0].type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                img.src = e.target.result;
                preview.classList.remove('hidden');
            }
            reader.readAsDataURL(input.files[0]);
        } else {
            preview.classList.add('hidden');
        }
    }

    // Clipboard Paste Fix
    document.addEventListener('paste', (e) => {
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        for (let index in items) {
            const item = items[index];
            if (item.kind === 'file' || item.type.indexOf('image') !== -1) {
                const blob = item.getAsFile();
                if (!blob) continue;
                
                const dataTransfer = new DataTransfer();
                const extension = blob.type.includes('/') ? '.' + blob.type.split('/')[1] : '.png';
                const fileName = blob.name || 'clipboard-' + Date.now() + extension;
                dataTransfer.items.add(new File([blob], fileName, { type: blob.type }));
                
                // CRITICAL: Change type first, THEN set files, because onTypeChange clears file input
                typeSelect.value = 'file';
                onTypeChange();
                
                fileInputEl.files = dataTransfer.files;
                handleFileSelect(fileInputEl);
                e.preventDefault();
                break;
            }
        }
    });

    // Form Submit
    document.getElementById('create-form').onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        if (formData.get('fast_forward') === 'true') formData.set('fast_forward', '1');
        else formData.set('fast_forward', '0');

        try {
            const response = await fetch('/items', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (response.ok) {
                showNotification('Created successfully!');
                document.getElementById('result').classList.remove('hidden');
                document.getElementById('result-url').value = data.uri;
                
                const rawUrl = data.raw_uri;
                document.getElementById('result-raw-url').value = rawUrl;
                document.querySelectorAll('.raw-url-placeholder').forEach(el => el.textContent = rawUrl);
            } else {
                showNotification('Error: ' + data.message, 'error');
            }
        } catch (err) {
            showNotification('Network error', 'error');
        }
    };

    // Initial state
    onTypeChange();

    // Check configuration for unlimited options
    loadConfig().then(config => {
        if (config) {
            if (!config.ENABLE_UNLIMITED_USAGE) {
                document.getElementById('access-unlimited')?.remove();
            }
            if (!config.ENABLE_UNLIMITED_AGE) {
                document.getElementById('time-unlimited')?.remove();
            }
        }
    });
}

function clearForm() {
    const typeSelect = document.getElementById('type');
    const currentType = typeSelect ? typeSelect.value : null;

    document.getElementById('create-form').reset();

    if (typeSelect && currentType) {
        typeSelect.value = currentType;
    }

    document.getElementById('image-preview').classList.add('hidden');
    document.getElementById('result').classList.add('hidden');
    
    // We need to trigger the UI update
    if (typeSelect) {
        typeSelect.dispatchEvent(new Event('change'));
    }
}

function copyResult(elementId) {
    const el = document.getElementById(elementId || 'result-url');
    el.select();
    document.execCommand('copy');
    showNotification('Copied to clipboard!');
    // Visual feedback
    const btn = el.nextElementSibling;
    if (btn && btn.tagName === 'BUTTON') {
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => btn.textContent = originalText, 2000);
    }
}

// View Logic
async function loadViewItem(id) {
    const viewContent = document.getElementById('view-content');
    const viewCard = document.getElementById('view-card');
    const viewTitle = document.getElementById('view-title');
    viewContent.innerHTML = 'Loading...';

    try {
        const response = await fetch('/api/items/' + id);
        if (!response.ok) {
            viewContent.innerHTML = `<p class="text-red-500">${response.status === 404 ? 'Item not found or expired.' : 'Error loading item.'}</p>`;
            return;
        }

        const item = await response.json();
        window.currentItem = item; // Store for copy/download

        // Show raw link
        const rawContainer = document.getElementById('raw-link-container');
        if (rawContainer) {
            rawContainer.classList.remove('hidden');
            document.getElementById('view-raw-url').value = item.raw_uri;
        }
        
        if (item.type === 'text') {
            const pre = document.createElement('pre');
            const code = document.createElement('code');
            const syntax = item.syntax || 'plain';
            code.className = 'language-' + syntax; 
            code.textContent = item.content;
            pre.appendChild(code);
            viewContent.innerHTML = '';
            viewContent.appendChild(pre);
            
            // Add Copy/Download buttons for text
            const actions = document.createElement('div');
            actions.className = 'flex gap-2 mt-4';
            actions.innerHTML = `
                <button onclick="copyAll()" class="bg-gray-200 dark:bg-gray-700 px-4 py-2 rounded hover:bg-gray-300 transition text-sm">Copy All</button>
                <button onclick="downloadAsTxt()" class="bg-gray-200 dark:bg-gray-700 px-4 py-2 rounded hover:bg-gray-300 transition text-sm">Download as .txt</button>
            `;
            viewContent.appendChild(actions);

            if (window.Prism) {
                Prism.highlightElement(code);
            }
        } else if (item.type === 'link') {
            viewCard.classList.remove('max-w-2xl');
            viewCard.classList.add('max-w-sm', 'mx-auto');
            viewContent.innerHTML = `
               <div class="text-center p-4">
                   <p class="text-sm text-gray-500 mb-2">Shortened Link</p>
                   <a href="${item.content}" class="text-blue-500 font-bold break-all hover:underline text-lg">${item.content}</a>
                   <div class="mt-4">
                       <a href="${item.content}" class="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg font-bold">Go to Link</a>
                   </div>
               </div>
            `;
        } else if (item.type === 'image') {
            const blob = await (await fetch(`data:${item.mimetype || 'image/png'};base64,${item.content}`)).blob();
            const blobUrl = URL.createObjectURL(blob);
            const img = document.createElement('img');
            img.src = blobUrl;
            img.className = 'w-full h-auto rounded-lg shadow-lg';
            viewContent.innerHTML = '';
            viewContent.appendChild(img);

            // Add Download button for image
            const actions = document.createElement('div');
            actions.className = 'flex gap-2 mt-4';
            actions.innerHTML = `
                <a href="${blobUrl}" download="${item.filename || 'image.png'}" class="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-blue-700 transition text-sm">Download Image</a>
            `;
            viewContent.appendChild(actions);
        } else {
            const blob = await (await fetch(`data:${item.mimetype || 'application/octet-stream'};base64,${item.content}`)).blob();
            const blobUrl = URL.createObjectURL(blob);
            viewContent.innerHTML = `
                <div class="text-center py-8">
                    <div class="text-5xl mb-4">📁</div>
                    <p class="mb-4 font-semibold">${item.filename}</p>
                    <a href="${blobUrl}" download="${item.filename}" class="bg-blue-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-blue-700">Download File</a>
                </div>
            `;
        }
    } catch (err) {
        console.error(err);
        viewContent.innerHTML = 'Error loading item.';
    }
}

function copyAll() {
    if (window.currentItem && window.currentItem.content) {
        navigator.clipboard.writeText(window.currentItem.content);
        showNotification('Copied to clipboard!');
    }
}

function downloadAsTxt() {
    if (window.currentItem && window.currentItem.content) {
        const blob = new Blob([window.currentItem.content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = (window.currentItem.id || 'item') + '.txt';
        a.click();
        window.URL.revokeObjectURL(url);
    }
}
