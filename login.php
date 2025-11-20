<?php
require_once 'config.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    
    $correct_username = getenv('APP_USERNAME');
    $correct_password = getenv('APP_PASSWORD');

    if ($username === $correct_username && $password === $correct_password) {
        $_SESSION['logged_in'] = true;
        header('Location: index.php');
        exit;
    } else {
        $error = "Feil brukernavn eller passord";
    }
}
?>
<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Logg inn - Smidr</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <div class="login-container">
            <h1>Logg inn</h1>
            <?php if (isset($error)): ?>
                <p style="color: red;"><?php echo htmlspecialchars($error); ?></p>
            <?php endif; ?>
            <form method="POST">
                <input type="text" name="username" placeholder="Brukernavn" required>
                <input type="password" name="password" placeholder="Passord" required>
                <button type="submit">Logg inn</button>
            </form>
        </div>
    </div>
</body>
</html>
