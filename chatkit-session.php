<?php
require_once 'config.php';

header('Content-Type: application/json');

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    http_response_code(401);
    echo json_encode(['error' => 'Unauthorized']);
    exit;
}

$apiKey = getenv('OPENAI_API_KEY') ?: ($_ENV['OPENAI_API_KEY'] ?? ($_SERVER['OPENAI_API_KEY'] ?? null));
$workflowId = getenv('WORKFLOW_ID') ?: ($_ENV['WORKFLOW_ID'] ?? ($_SERVER['WORKFLOW_ID'] ?? null));

if (!$apiKey || !$workflowId) {
    http_response_code(500);
    echo json_encode(['error' => 'Configuration missing']);
    exit;
}

// Create a ChatKit session
$url = 'https://api.openai.com/v1/chatkit/sessions';

$data = [
    'workflow_id' => $workflowId
];

$headers = [
    'Authorization: Bearer ' . $apiKey,
    'Content-Type: application/json',
    'OpenAI-Beta: chatkit_beta=v1'
];

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($httpCode !== 200) {
    http_response_code($httpCode);
    echo json_encode(['error' => 'Failed to create ChatKit session', 'details' => json_decode($response, true)]);
    exit;
}

$sessionData = json_decode($response, true);
echo json_encode(['client_secret' => $sessionData['client_secret']]);
?>
