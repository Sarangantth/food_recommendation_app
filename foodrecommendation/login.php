<?php
// Database connection
$host = 'localhost';
$db = 'MySQL80';
$user = 'root';  // your MySQL username
$pass = 'Deepikasaran@2305';  // your MySQL password

// Create connection
$conn = new mysqli($host, $user, $pass, $db);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $email = $conn->real_escape_string($_POST['email']);
    $password = $conn->real_escape_string($_POST['password']);

    // Get user from the database
    $sql = "SELECT * FROM users WHERE email='$email'";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        $user = $result->fetch_assoc();
        // Verify password
        if (password_verify($password, $user['password'])) {
            // Successful login, you can start the session and redirect the user
            session_start();
            $_SESSION['user_id'] = $user['id'];
            $_SESSION['username'] = $user['username'];
            header("Location: dashboard.php");  // Redirect to a dashboard or another page
        } else {
            echo "Invalid password";
        }
    } else {
        echo "No account found with this email";
    }
}

$conn->close();
?>
