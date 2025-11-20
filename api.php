<?php
require_once 'config.php';

header('Content-Type: application/json');

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    http_response_code(401);
    echo json_encode(['error' => 'Unauthorized']);
    exit;
}

$apiKey = getenv('OPENAI_API_KEY');
$assistantId = getenv('ASSISTANT_ID');

if (!$apiKey || !$assistantId) {
    http_response_code(500);
    echo json_encode(['error' => 'Configuration missing']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
$action = $input['action'] ?? '';

function callOpenAI($endpoint, $method = 'GET', $data = null) {
    global $apiKey;
    $url = 'https://api.openai.com/v1' . $endpoint;
    
    $headers = [
        'Authorization: Bearer ' . $apiKey,
        'Content-Type: application/json',
        'OpenAI-Beta: assistants=v2' 
    ];

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    
    if ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        if ($data) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        }
    }

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    return ['code' => $httpCode, 'body' => json_decode($response, true)];
}

if ($action === 'sendMessage') {
    $message = $input['message'] ?? '';
    $threadId = $_SESSION['thread_id'] ?? null;

    // 1. Create Thread if not exists
    if (!$threadId) {
        $resp = callOpenAI('/threads', 'POST');
        if ($resp['code'] !== 200) {
            echo json_encode(['error' => 'Failed to create thread', 'details' => $resp['body']]);
            exit;
        }
        $threadId = $resp['body']['id'];
        $_SESSION['thread_id'] = $threadId;
    }

    // 2. Add Message
    $resp = callOpenAI("/threads/$threadId/messages", 'POST', [
        'role' => 'user',
        'content' => $message
    ]);
    if ($resp['code'] !== 200) {
        echo json_encode(['error' => 'Failed to send message', 'details' => $resp['body']]);
        exit;
    }

    // 3. Run Assistant
    $resp = callOpenAI("/threads/$threadId/runs", 'POST', [
        'assistant_id' => $assistantId
    ]);
    if ($resp['code'] !== 200) {
        echo json_encode(['error' => 'Failed to start run', 'details' => $resp['body']]);
        exit;
    }

    echo json_encode(['status' => 'queued', 'run_id' => $resp['body']['id'], 'thread_id' => $threadId]);

} elseif ($action === 'checkStatus') {
    $threadId = $_SESSION['thread_id'] ?? null;
    $runId = $input['run_id'] ?? null;

    if (!$threadId || !$runId) {
        echo json_encode(['error' => 'Missing thread_id or run_id']);
        exit;
    }

    $resp = callOpenAI("/threads/$threadId/runs/$runId", 'GET');
    
    if (!isset($resp['body']['status'])) {
        echo json_encode(['error' => 'Invalid API response', 'details' => $resp]);
        exit;
    }

    $status = $resp['body']['status'];

    if ($status === 'completed') {
        // Get messages
        $msgResp = callOpenAI("/threads/$threadId/messages", 'GET');
        $messages = $msgResp['body']['data'];
        
        // Get the latest message from assistant
        $latestResponse = '';
        foreach ($messages as $msg) {
            if ($msg['role'] === 'assistant') {
                foreach ($msg['content'] as $content) {
                    if ($content['type'] === 'text') {
                        $latestResponse = $content['text']['value'];
                        break 2;
                    }
                }
            }
        }
        
        echo json_encode(['status' => 'completed', 'response' => $latestResponse]);
    } else {
        echo json_encode(['status' => $status]);
    }

} else {
    echo json_encode(['error' => 'Invalid action']);
}
?>
