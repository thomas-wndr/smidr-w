<!DOCTYPE html>
<html lang="no">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KI - Smidr.org</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: white;
            color: black;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        header {
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        h1 {
            font-size: 2rem;
            font-weight: 600;
            flex-grow: 1;
        }

        .logout-btn {
            background-color: black;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background-color 0.3s;
        }

        .logout-btn:hover {
            background-color: #333;
        }

        .chat-container {
            flex: 1;
            display: flex;
            justify-content: center;
            padding: 20px;
            overflow: hidden;
        }

        #chatkit-container {
            width: 100%;
            max-width: 750px;
            height: 100%;
        }

        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            font-size: 1.2rem;
            color: #666;
        }
    </style>
</head>

<body>
    <header>
        <h1>KI</h1>
        <button class="logout-btn">Logg ut</button>
    </header>
    <div class="chat-container">
        <div id="chatkit-container">
            <div class="loading">Laster chat...</div>
        </div>
    </div>

    <!-- ChatKit Web Component -->
    <script type="module">
        // Import ChatKit
        import 'https://cdn.jsdelivr.net/npm/@openai/chatkit@latest/dist/chatkit.js';

        async function initializeChatKit() {
            try {
                // Get client_secret from backend
                const response = await fetch('chatkit-session.php');
                const data = await response.json();

                if (data.error) {
                    document.getElementById('chatkit-container').innerHTML =
                        `<div class="loading">Feil: ${data.error}</div>`;
                    return;
                }

                // Clear loading message
                document.getElementById('chatkit-container').innerHTML = '';

                // Create ChatKit element
                const chatkit = document.createElement('openai-chatkit');
                chatkit.setAttribute('client-secret', data.client_secret);

                // Optional: Customize appearance
                chatkit.style.width = '100%';
                chatkit.style.height = '100%';
                chatkit.style.borderRadius = '12px';
                chatkit.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';

                document.getElementById('chatkit-container').appendChild(chatkit);
            } catch (error) {
<!DOCTYPE html>
<html lang="no">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KI - Smidr.org</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: white;
            color: black;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        header {
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        h1 {
            font-size: 2rem;
            font-weight: 600;
            flex-grow: 1;
        }

        .logout-btn {
            background-color: black;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background-color 0.3s;
        }

        .logout-btn:hover {
            background-color: #333;
        }

        .chat-container {
            flex: 1;
            display: flex;
            justify-content: center;
            padding: 20px;
            overflow: hidden;
        }

        #chatkit-container {
            width: 100%;
            max-width: 750px;
            height: 100%;
        }

        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            font-size: 1.2rem;
            color: #666;
        }
    </style>
</head>

<body>
    <header>
        <h1>KI</h1>
        <button class="logout-btn" onclick="logout()">Logg ut</button>
    </header>
    <div class="chat-container">
        <div id="chatkit-container">
            <div class="loading">Laster chat...</div>
        </div>
    </div>

    <!-- ChatKit Web Component -->
    <script type="module">
        // Import ChatKit
        import 'https://cdn.jsdelivr.net/npm/@openai/chatkit@latest/dist/chatkit.js';

        async function initializeChatKit() {
            try {
                // Get client_secret from backend
                const response = await fetch('chatkit-session.php');
                const data = await response.json();

                if (data.error) {
                    document.getElementById('chatkit-container').innerHTML =
                        `<div class="loading">Feil: ${data.error}</div>`;
                    return;
                }

                // Clear loading message
                document.getElementById('chatkit-container').innerHTML = '';

                // Create ChatKit element
                const chatkit = document.createElement('openai-chatkit');
                chatkit.setAttribute('client-secret', data.client_secret);

                // Optional: Customize appearance
                chatkit.style.width = '100%';
                chatkit.style.height = '100%';
                chatkit.style.borderRadius = '12px';
                chatkit.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';

                document.getElementById('chatkit-container').appendChild(chatkit);
            } catch (error) {
                console.error('Failed to initialize ChatKit:', error);
                document.getElementById('chatkit-container').innerHTML =
                    '<div class="loading">Kunne ikke laste chat. Prøv å laste siden på nytt.</div>';
            }
        }

        // Initialize when page loads
        initializeChatKit();

        // Logout function
        document.querySelector('.logout-btn').addEventListener('click', () => {
            window.location.href = 'logout.php';
        });
    </script>
</body>

</html>