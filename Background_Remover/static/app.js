const fileInput = document.querySelector('#file-input');
const dropzone = document.querySelector('#dropzone');
const workspace = document.querySelector('#workspace');
const originalPreview = document.querySelector('#original-preview');
const resultPreview = document.querySelector('#result-preview');
const previewGrid = document.querySelector('.preview-grid');
const resultPlaceholder = document.querySelector('#result-placeholder');
const removeButton = document.querySelector('#remove-button');
const downloadButton = document.querySelector('#download-button');
const message = document.querySelector('#message');
const fileName = document.querySelector('#file-name');

let selectedFile = null;
let originalUrl = null;
let resultUrl = null;

function clearResult() {
  if (resultUrl) URL.revokeObjectURL(resultUrl);
  resultUrl = null;
  resultPreview.removeAttribute('src');
  resultPreview.hidden = true;
  resultPlaceholder.hidden = false;
  downloadButton.hidden = true;
}

function chooseFile(file) {
  if (!file) return;
  if (!file.type.startsWith('image/')) {
    setMessage('Choose an image file, such as JPG, PNG, WebP, or HEIC.', true);
    return;
  }
  if (file.size > 12 * 1024 * 1024) {
    setMessage('That file is over the 12 MB upload limit.', true);
    return;
  }

  selectedFile = file;
  if (originalUrl) URL.revokeObjectURL(originalUrl);
  previewGrid.style.removeProperty('--preview-ratio');
  originalUrl = URL.createObjectURL(file);
  originalPreview.onload = () => {
    previewGrid.style.setProperty('--preview-ratio', `${originalPreview.naturalWidth} / ${originalPreview.naturalHeight}`);
  };
  originalPreview.src = originalUrl;
  fileName.textContent = file.name;
  dropzone.hidden = true;
  workspace.hidden = false;
  removeButton.hidden = false;
  clearResult();
  setMessage('Ready when you are.');
}

function setMessage(text, isError = false) {
  message.textContent = text;
  message.classList.toggle('is-error', isError);
}

dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    fileInput.click();
  }
});
fileInput.addEventListener('change', () => chooseFile(fileInput.files[0]));
document.querySelector('#replace-button').addEventListener('click', () => fileInput.click());

for (const eventName of ['dragenter', 'dragover']) {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.add('is-dragging');
  });
}
for (const eventName of ['dragleave', 'drop']) {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.remove('is-dragging');
  });
}
dropzone.addEventListener('drop', (event) => chooseFile(event.dataTransfer.files[0]));

removeButton.addEventListener('click', async () => {
  if (!selectedFile) return;
  const formData = new FormData();
  formData.append('image', selectedFile);
  removeButton.disabled = true;
  removeButton.querySelector('.button-label').textContent = 'Removing background...';
  setMessage('Processing your image. Larger photos can take a little longer.');

  try {
    const response = await fetch('/api/remove-background', { method: 'POST', body: formData });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'The image could not be processed.');
    }
    const resultBlob = await response.blob();
    clearResult();
    resultUrl = URL.createObjectURL(resultBlob);
    resultPreview.src = resultUrl;
    resultPreview.hidden = false;
    resultPlaceholder.hidden = true;
    downloadButton.href = resultUrl;
    downloadButton.hidden = false;
    removeButton.hidden = true;
    setMessage('Background removed. Your transparent PNG is ready.');
  } catch (error) {
    setMessage(error.message || 'Something went wrong. Please try again.', true);
  } finally {
    removeButton.disabled = false;
    removeButton.querySelector('.button-label').textContent = 'Remove background';
  }
});