<?php
// Database configuration
$servername = "%saran"; // or "127.0.0.1"
$username = "saran"; // default username for XAMPP
$password = "Deepikasaran@2305"; // default password for XAMPP (leave empty if not set)
$dbname = "user_management"; // replace with your database name

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Check if the form was submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Retrieve form data
    $flavor = $_POST['flavor'];
    $food_type = $_POST['food_type'];
    $mood = $_POST['mood'];
    $weather = $_POST['weather'];
    $companions = $_POST['companions'];
    $dining_place = $_POST['dining_place'];

    // Prepare and bind
    $stmt = $conn->prepare("INSERT INTO food_preferences (flavor, food_type, mood, weather, companions, dining_place) VALUES (?, ?, ?, ?, ?, ?)");
    $stmt->bind_param("ssssss", $flavor, $food_type, $mood, $weather, $companions, $dining_place);

    // Execute the statement
    if ($stmt->execute()) {
        echo "Preferences submitted successfully!";
    } else {
        echo "Error: " . $stmt->error;
    }

    // Close the statement
    $stmt->close();
}

// Close the connection
$conn->close();
?>
