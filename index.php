<?php
require_once 'config.php';

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header('Location: login.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smidr Agent</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <div class="chat-wrapper">
            <div class="chat-header" style="display: flex; justify-content: space-between; align-items: center;">
                <h1 style="margin: 0; flex-grow: 1; text-align: center;">KI</h1>
                <a href="logout.php" style="text-decoration: none; color: #000; font-size: 0.9em;">Logg ut</a>
            </div>
            <div class="chat-box" id="chat-box">
                <!-- Messages will appear here -->
                <div class="message assistant">Hei! Hvordan kan jeg hjelpe deg i dag?</div>
            </div>
            <form class="input-area" id="chat-form">
                <input type="text" id="user-input" placeholder="Skriv en melding..." autocomplete="off" required>
                <button type="submit">Send</button>
            </form>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>
