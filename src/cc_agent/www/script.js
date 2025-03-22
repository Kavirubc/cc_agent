// filepath: /Users/kaviruhapuarachchi/Downloads/cc_agent/src/cc_agent/www/script.js
document.getElementById('crewForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });

    fetch('http://localhost:8000/execute_crew', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const reader = response.body.getReader();
            return new ReadableStream({
                start(controller) {
                    function push() {
                        reader.read().then(({ done, value }) => {
                            if (done) {
                                controller.close();
                                return;
                            }
                            controller.enqueue(new TextDecoder().decode(value));
                            push();
                        })
                    }
                    push();
                }
            });
        })
        .then(stream => {
            const outputContent = document.getElementById('outputContent');
            const reader = stream.getReader();
            let markdownText = '';
            const updatesContainer = document.getElementById('updates'); // Get the updates container

            return new Promise((resolve, reject) => {
                function read() {
                    reader.read().then(({ done, value }) => {
                        if (done) {
                            // Parse Markdown and render as HTML
                            outputContent.innerHTML = marked.parse(markdownText);
                            resolve();
                            return;
                        }
                        // Check if the value is an agent/task update
                        if (value.startsWith("Agent:")) {
                            // Display the update in the updates container
                            updatesContainer.textContent += value;
                        } else {
                            markdownText += value;
                        }
                        read();
                    }, error => {
                        reject(error);
                    });
                }
                read();
            });
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('outputContent').textContent = 'Error: ' + error;
        });
});