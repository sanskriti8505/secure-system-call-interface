document.addEventListener('DOMContentLoaded', () => {
    // Tab switching logic
    const tabs = document.querySelectorAll('.action-tab');
    const forms = document.querySelectorAll('.action-form');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active state from all tabs
            tabs.forEach(t => {
                t.classList.remove('bg-cyber-border', 'text-white', 'active');
                t.classList.add('bg-cyber-dark', 'text-gray-400', 'border-cyber-border');
            });
            
            // Add active state to clicked tab
            tab.classList.remove('bg-cyber-dark', 'text-gray-400', 'border-cyber-border');
            tab.classList.add('bg-cyber-border', 'text-white', 'active');

            // Hide all forms
            forms.forEach(f => {
                f.classList.remove('active');
                f.classList.add('hidden');
            });

            // Show target form
            const targetId = tab.getAttribute('data-target');
            const targetForm = document.getElementById(targetId);
            targetForm.classList.remove('hidden');
            // Small delay to allow display:block to apply before opacity transition
            setTimeout(() => {
                targetForm.classList.add('active');
            }, 10);
        });
    });

    // Form submission logic via AJAX
    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const action = form.getAttribute('data-action');
            const formData = new FormData(form);
            const data = {
                action: action,
                target: formData.get('target') || '',
                content: formData.get('content') || ''
            };

            const consoleOutput = document.getElementById('console-output');
            const statusIndicator = document.getElementById('status-indicator');
            
            // Loading state
            consoleOutput.innerHTML = `
                <div class="flex items-center justify-center h-full text-cyber-accent">
                    <i class="fas fa-circle-notch fa-spin text-3xl mr-3"></i>
                    <span>Executing syscall...</span>
                </div>
            `;
            statusIndicator.className = 'hidden';

            try {
                const response = await fetch('/api/execute', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                // Update status indicator
                statusIndicator.classList.remove('hidden');
                if (result.status === 'success') {
                    statusIndicator.className = 'flex items-center px-3 py-1 rounded text-xs font-bold uppercase tracking-wider bg-green-900/50 text-green-400 border border-green-500/50';
                    statusIndicator.innerHTML = '<i class="fas fa-check mr-2"></i> SUCCESS';
                } else if (result.status === 'denied') {
                    statusIndicator.className = 'flex items-center px-3 py-1 rounded text-xs font-bold uppercase tracking-wider bg-red-900/50 text-red-400 border border-red-500/50';
                    statusIndicator.innerHTML = '<i class="fas fa-ban mr-2"></i> ACCESS DENIED';
                } else {
                    statusIndicator.className = 'flex items-center px-3 py-1 rounded text-xs font-bold uppercase tracking-wider bg-yellow-900/50 text-yellow-400 border border-yellow-500/50';
                    statusIndicator.innerHTML = '<i class="fas fa-exclamation-triangle mr-2"></i> ERROR';
                }

                // Format output
                let outputHtml = `<div class="mb-4 pb-2 border-b border-cyber-border/50">
                    <strong class="text-gray-400">Command:</strong> <span class="text-white">${action.toUpperCase()} ${data.target}</span><br>
                    <strong class="text-gray-400">Message:</strong> <span class="${result.status === 'success' ? 'text-green-400' : 'text-red-400'}">${result.message}</span>
                </div>`;

                if (result.data) {
                    // Escape HTML to prevent XSS if rendering command output
                    const escapedData = result.data
                        .replace(/&/g, "&amp;")
                        .replace(/</g, "&lt;")
                        .replace(/>/g, "&gt;")
                        .replace(/"/g, "&quot;")
                        .replace(/'/g, "&#039;");
                        
                    outputHtml += `<pre class="text-gray-300 font-mono text-sm leading-relaxed">${escapedData}</pre>`;
                }

                consoleOutput.innerHTML = outputHtml;
                
            } catch (error) {
                statusIndicator.classList.remove('hidden');
                statusIndicator.className = 'flex items-center px-3 py-1 rounded text-xs font-bold uppercase tracking-wider bg-red-900/50 text-red-400 border border-red-500/50';
                statusIndicator.innerHTML = '<i class="fas fa-times mr-2"></i> NETWORK ERROR';
                
                consoleOutput.innerHTML = `<div class="text-red-400"><i class="fas fa-exclamation-circle mr-2"></i> Failed to communicate with the server: ${error.message}</div>`;
            }
        });
    });
});
