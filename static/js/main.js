// VisualTales - Main JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize form handlers
    initializeCreateForm();
    initializePanelGeneration();
    initializeAudioPlayers();
    initializeTooltips();
    initializeConfirmDialogs();
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        });
    }, 5000);
}

function initializeCreateForm() {
    const createForm = document.getElementById('createComicForm');
    if (createForm) {
        createForm.addEventListener('submit', function(e) {
            const title = document.getElementById('title');
            if (title && !title.value.trim()) {
                e.preventDefault();
                showAlert('Comic title is required', 'danger');
                title.focus();
                return false;
            }
            
            // Show loading state
            const submitBtn = createForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Creating...';
            }
        });
    }
}

function initializePanelGeneration() {
    const generateForms = document.querySelectorAll('.generate-panel-form');
    generateForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const description = form.querySelector('textarea[name="scene_description"]');
            if (description && !description.value.trim()) {
                e.preventDefault();
                showAlert('Scene description is required', 'danger');
                description.focus();
                return false;
            }
            
            // Show loading state
            showLoadingSpinner(form);
            
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Generating...';
            }
        });
    });
    
    // Handle edit panel forms
    const editForms = document.querySelectorAll('.edit-panel-form');
    editForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const instruction = form.querySelector('input[name="edit_instruction"]');
            if (instruction && !instruction.value.trim()) {
                e.preventDefault();
                showAlert('Edit instruction is required', 'danger');
                instruction.focus();
                return false;
            }
            
            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Editing...';
            }
        });
    });
    
    // Handle narration forms
    const narrationForms = document.querySelectorAll('.narration-form');
    narrationForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const narrationText = form.querySelector('textarea[name="narration_text"]');
            if (narrationText && !narrationText.value.trim()) {
                e.preventDefault();
                showAlert('Narration text is required', 'danger');
                narrationText.focus();
                return false;
            }
            
            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Generating Audio...';
            }
        });
    });
}

function initializeAudioPlayers() {
    const audioPlayers = document.querySelectorAll('.audio-player');
    audioPlayers.forEach(function(player) {
        player.addEventListener('play', function() {
            // Pause other audio players when one starts playing
            audioPlayers.forEach(function(otherPlayer) {
                if (otherPlayer !== player && !otherPlayer.paused) {
                    otherPlayer.pause();
                }
            });
        });
        
        player.addEventListener('error', function() {
            console.error('Error loading audio file:', player.src);
            const parentPanel = player.closest('.comic-panel');
            if (parentPanel) {
                const errorMsg = document.createElement('div');
                errorMsg.className = 'alert alert-warning alert-sm';
                errorMsg.textContent = 'Audio file could not be loaded';
                player.parentNode.insertBefore(errorMsg, player.nextSibling);
                player.style.display = 'none';
            }
        });
    });
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function initializeConfirmDialogs() {
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const itemName = button.dataset.itemName || 'this item';
            if (!confirm(`Are you sure you want to delete ${itemName}? This action cannot be undone.`)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

function showLoadingSpinner(container) {
    const spinner = container.querySelector('.loading-spinner');
    if (spinner) {
        spinner.classList.add('show');
    }
}

function hideLoadingSpinner(container) {
    const spinner = container.querySelector('.loading-spinner');
    if (spinner) {
        spinner.classList.remove('show');
    }
}

function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        if (alertDiv.parentNode) {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }
    }, 5000);
}

function toggleCharacterForm() {
// Show Edit Character Form
function showEditCharacterForm(name, description) {
    const editForm = document.getElementById('editCharacterForm');
    const formElem = document.getElementById('editCharacterFormElem');
    if (editForm && formElem) {
        editForm.style.display = 'block';
        document.getElementById('edit_character_name').value = name;
        document.getElementById('edit_character_description').value = description;
        // Set form action
        const comicId = document.getElementById('edit_character_name').dataset.comicId || window.comicId;
        formElem.action = `/comic/${comicId}/edit_character/${encodeURIComponent(name)}`;
    }
}

function toggleEditCharacterForm() {
    const editForm = document.getElementById('editCharacterForm');
    if (editForm) {
        editForm.style.display = 'none';
    }
}
    const characterForm = document.getElementById('characterForm');
    if (characterForm) {
        if (characterForm.style.display === 'none' || !characterForm.style.display) {
            characterForm.style.display = 'block';
            characterForm.classList.add('fade-in');
        } else {
            characterForm.style.display = 'none';
            characterForm.classList.remove('fade-in');
        }
    }
}

function previewPanel(panelId) {
    const panel = document.querySelector(`[data-panel-id="${panelId}"]`);
    if (panel) {
        const modal = new bootstrap.Modal(document.getElementById('panelPreviewModal'));
        const modalBody = document.querySelector('#panelPreviewModal .modal-body');
        
        // Clone panel content for preview
        const panelClone = panel.cloneNode(true);
        modalBody.innerHTML = '';
        modalBody.appendChild(panelClone);
        
        modal.show();
    }
}

function exportComic(comicId) {
    // Show loading state
    const exportBtn = document.querySelector(`[onclick="exportComic(${comicId})"]`);
    if (exportBtn) {
        exportBtn.disabled = true;
        exportBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Exporting...';
        
        // Re-enable button after 10 seconds (in case of slow export)
        setTimeout(function() {
            exportBtn.disabled = false;
            exportBtn.innerHTML = '<i data-feather="download"></i> Export PDF';
            feather.replace();
        }, 10000);
    }
    
    // Redirect to export endpoint
    window.location.href = `/comic/${comicId}/export_pdf`;
}

// Character management functions
function addCharacter() {
    const form = document.getElementById('characterForm');
    const name = document.getElementById('character_name');
    
    if (form && name) {
        if (!name.value.trim()) {
            showAlert('Character name is required', 'danger');
            name.focus();
            return false;
        }
        
        form.submit();
    }
}

// Panel control functions
function showEditForm(panelId) {
    const editForm = document.getElementById(`editForm_${panelId}`);
    if (editForm) {
        editForm.style.display = editForm.style.display === 'none' ? 'block' : 'none';
    }
}

function showNarrationForm(panelId) {
    const narrationForm = document.getElementById(`narrationForm_${panelId}`);
    if (narrationForm) {
        narrationForm.style.display = narrationForm.style.display === 'none' ? 'block' : 'none';
    }
}

// Initialize Feather icons when they're loaded
document.addEventListener('DOMContentLoaded', function() {
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
});
