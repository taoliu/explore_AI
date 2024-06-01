$(document).ready(function(){
    // ASCII Spinner
    let spinner = ['|', '/', '-', '\\'];
    let spinnerIndex = 0;
    let spinnerInterval;

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

    // Store conversation history
    let conversationHistory = [];

    // Text Generation Form Submission
    $('#generateForm').on('submit', function(event){
        event.preventDefault();
        const instruction = $('#instructionInput').val();
        
        startLoading();

        // Add the current user message to the conversation history
        conversationHistory.push({"role": "user", "content": instruction});
        
        // Construct the messages array
        const messages = conversationHistory;

        $.ajax({
            url: 'http://localhost:8080/v1/chat/completions',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                messages: messages,
                temperature: 0.1,
                max_tokens: 8000
            }),
            success: function(response){
                stopLoading();
                let historyDiv = $('#conversationHistory');
                if (response.choices && response.choices.length > 0) {
                    const generated_text = response.choices[0].message.content.trim();
                    const renderedHTML = marked.parse(generated_text);

                    // Add the assistant's response to the conversation history
                    conversationHistory.push({"role": "assistant", "content": generated_text});

                    // Update the conversation history display
                    historyDiv.prepend(`<div class="message-box user-message"><strong>You:</strong> ${marked.parse(instruction)}</div>`);
                    historyDiv.prepend(`<div class="message-box system-message"><strong>System:</strong> ${renderedHTML}</div>`);
                    MathJax.typesetPromise(); // Re-render MathJax content
                } else {
                    historyDiv.prepend('<p>No generated text found.</p>');
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
        conversationHistory = [];
        $('#conversationHistory').empty();
        $('#instructionInput').val('');
    });

    // Save Button Click Handler
    $('#saveButton').on('click', function(){
        const blob = new Blob([JSON.stringify(conversationHistory, null, 2)], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'conversation_history.txt';
        a.click();
        URL.revokeObjectURL(url);
    });
});
