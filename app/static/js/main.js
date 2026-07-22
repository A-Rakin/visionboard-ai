/* VisionBoard AI — Main Client Interactions */

document.addEventListener('DOMContentLoaded', () => {
  initDragAndDrop();
  initCopyButtons();
  initFavoriteButtons();
  initCollectionForms();
});

// 1. Drag & Drop File Upload
function initDragAndDrop() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener('click', () => fileInput.click());

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    }, false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      fileInput.files = files;
      handleFileUpload(files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (fileInput.files.length > 0) {
      handleFileUpload(fileInput.files[0]);
    }
  });
}

function handleFileUpload(file) {
  const statusArea = document.getElementById('uploadStatus');
  if (statusArea) {
    statusArea.innerHTML = `
      <div class="d-flex align-items-center justify-content-center gap-3 text-info mt-3">
        <div class="spinner-border text-info" role="status"></div>
        <span>Uploading & AI Pipeline Processing Image... Please wait</span>
      </div>
    `;
  }

  const formData = new FormData();
  formData.append('image', file);

  fetch('/upload', {
    method: 'POST',
    body: formData,
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      showToast('Image Processed!', 'AI analysis completed. Redirecting...', 'success');
      setTimeout(() => {
        window.location.href = data.redirect_url;
      }, 800);
    } else {
      showToast('Upload Failed', data.error || 'Failed to upload image.', 'danger');
      if (statusArea) statusArea.innerHTML = '';
    }
  })
  .catch(err => {
    console.error(err);
    showToast('Error', 'An error occurred while uploading.', 'danger');
    if (statusArea) statusArea.innerHTML = '';
  });
}

// 2. Clipboard Helpers
function initCopyButtons() {
  document.querySelectorAll('.btn-copy').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-copy-target');
      let text = '';
      if (targetId) {
        const elem = document.getElementById(targetId);
        text = elem ? elem.innerText : '';
      } else {
        text = btn.getAttribute('data-copy-text') || '';
      }

      if (text) {
        navigator.clipboard.writeText(text).then(() => {
          showToast('Copied!', `Copied to clipboard: "${text}"`, 'info');
        });
      }
    });
  });
}

// 3. Favorite Toggle
function initFavoriteButtons() {
  document.querySelectorAll('.btn-favorite').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const imageId = btn.getAttribute('data-image-id');
      fetch(`/image/${imageId}/favorite`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            const icon = btn.querySelector('i');
            if (data.is_favorite) {
              icon.classList.remove('bi-heart');
              icon.classList.add('bi-heart-fill', 'text-danger');
              showToast('Favorites', 'Saved to your favorites!', 'success');
            } else {
              icon.classList.remove('bi-heart-fill', 'text-danger');
              icon.classList.add('bi-heart');
              showToast('Favorites', 'Removed from favorites.', 'info');
            }
          }
        });
    });
  });
}

// 4. Collection Form AJAX
function initCollectionForms() {
  document.querySelectorAll('.form-add-collection').forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      fetch('/collections/add_image', {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          showToast('Collection', data.message, 'success');
          const modal = bootstrap.Modal.getInstance(form.closest('.modal'));
          if (modal) modal.hide();
        }
      });
    });
  });
}

// Toast Notifications
function showToast(title, message, type='info') {
  const toastContainer = document.getElementById('toastContainer');
  if (!toastContainer) return;

  const bgClass = type === 'success' ? 'bg-success' : (type === 'danger' ? 'bg-danger' : 'bg-primary');
  
  const toastHtml = `
    <div class="toast align-items-center text-white ${bgClass} border-0 show" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          <strong>${title}:</strong> ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;

  const toastElem = document.createElement('div');
  toastElem.innerHTML = toastHtml;
  toastContainer.appendChild(toastElem.firstElementChild);

  setTimeout(() => {
    toastElem.remove();
  }, 4000);
}
