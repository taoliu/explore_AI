$(document).ready(function(){
    // ASCII Spinner
    let spinner = ['|', '/', '-', '\\'];
    let spinnerIndex = 0;
    let spinnerInterval;
    let currentSession = null;

    function startLoading() {
        $('#loading').show();
        spinnerInterval = setInterval(function() {
            $('#loading').text(spinner[spinnerIndex]);
            spinnerIndex = (spinnerIndex + 1) % spinner.length;
        }, 250);
    }

    function stopLoading() {
        clearInterval(spinnerInterval);
        $('#loading').hide();
    }

    // Initially hide the loading animation
    $('#loading').hide();

    // Load sessions into the select dropdown
    function loadSessions() {
        const sessionSelect = $('#sessionSelect');
        sessionSelect.empty();
        Object.keys(localStorage).forEach(function(key) {
            const sessionData = JSON.parse(localStorage.getItem(key));
            sessionSelect.append(new Option(sessionData.name, key));
        });
    }

    // Create a new session
    $('#newSessionButton').on('click', function() {
        const sessionName = prompt('Enter a name for the new session:');
        if (sessionName) {
            $.ajax({
                url: '/session',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({session_name: sessionName}),
                success: function(response) {
                    const sessionId = response.session_id;
                    localStorage.setItem(sessionId, JSON.stringify({name: sessionName, history: []}));
                    loadSessions();
                    currentSession = sessionId;
                    $('#sessionSelect').val(sessionId);
                    $('#conversationHistory').empty();
                }
            });
        }
    });

    // Load a session
    $('#sessionSelect').on('change', function() {
        currentSession = $(this).val();
        const sessionData = JSON.parse(localStorage.getItem(currentSession) || '{}');
        $('#conversationHistory').empty();
        sessionData.history.forEach(function(message) {
            const messageClass = message.role === 'user' ? 'user-message' : 'system-message';
            const label = message.role === 'user' ? 'You' : 'System';
            $('#conversationHistory').prepend(`<div class="message-box ${messageClass}"><strong>${label}:</strong> ${marked.parse(message.content)}</div>`);
        });
        MathJax.typesetPromise(); // Re-render MathJax content
    });

    // Delete a session
    $('#deleteSessionButton').on('click', function() {
        if (currentSession) {
            localStorage.removeItem(currentSession);
            loadSessions();
            $('#conversationHistory').empty();
            currentSession = null;
        }
    });

    // Text Generation Form Submission
    $('#generateForm').on('submit', function(event){
        event.preventDefault();
        const instruction = $('#instructionInput').val();
        
        startLoading();

        if (!currentSession) {
            alert('Please create or select a session first.');
            stopLoading();
            return;
        }

        const sessionData = JSON.parse(localStorage.getItem(currentSession) || '{}');
        sessionData.history.push({"role": "user", "content": instruction});
        localStorage.setItem(currentSession, JSON.stringify(sessionData));

        $.ajax({
            url: 'http://localhost:8080/v1/chat/completions',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                messages: sessionData.history,
                temperature: 0.1,
                max_tokens: 8000
            }),
            success: function(response){
                stopLoading();
                if (response.choices && response.choices.length > 0) {
                    const generated_text = response.choices[0].message.content.trim();
                    const renderedHTML = marked.parse(generated_text);

                    sessionData.history.push({"role": "assistant", "content": generated_text});
                    localStorage.setItem(currentSession, JSON.stringify(sessionData));

                    $('#conversationHistory').prepend(`<div class="message-box user-message"><strong>You:</strong> ${marked.parse(instruction)}</div>`);
                    $('#conversationHistory').prepend(`<div class="message-box system-message"><strong>System:</strong> ${renderedHTML}</div>`);
                    $('#instructionInput').val(''); // Clear the input field
                    MathJax.typesetPromise(); // Re-render MathJax content
                } else {
                    $('#conversationHistory').prepend('<p>No generated text found.</p>');
                }
            },
            error: function(error){
                stopLoading();
                console.error(error);
                alert('An error occurred. Please try again.');
            }
        });
    });

    // Reset Button Click Handler
    $('#resetButton').on('click', function(){
        if (currentSession) {
            const sessionData = JSON.parse(localStorage.getItem(currentSession) || '{}');
            sessionData.history = [];
            localStorage.setItem(currentSession, JSON.stringify(sessionData));
            $('#conversationHistory').empty();
        }
    });

    // Save Button Click Handler
    $('#saveButton').on('click', function(){
        if (currentSession) {
            const sessionData = localStorage.getItem(currentSession);
            const blob = new Blob([sessionData], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${JSON.parse(sessionData).name}_conversation_history.txt`;
            a.click();
            URL.revokeObjectURL(url);
        } else {
            alert('Please create or select a session first.');
        }
    });

    // Load initial sessions
    loadSessions();
});
