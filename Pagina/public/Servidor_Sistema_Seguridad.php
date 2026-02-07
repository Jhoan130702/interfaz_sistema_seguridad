<?php
$servername = "localhost"; // Cambia esto si tu base de datos está en otro servidor
$username = "tu_usuario"; // Tu usuario de MySQL
$password = "tu_contraseña"; // Tu contraseña de MySQL
$dbname = "mi_base_datos"; // Nombre de tu base de datos

// Crear conexión
$conn = new mysqli($servername, $username, $password, $dbname);

// Verificar conexión
if ($conn->connect_error) {
    die("Conexión fallida: " . $conn->connect_error);
}

// Obtener datos del ESP8266
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $valor = $_POST['data']; // Asegúrate de que 'data' coincida con lo que envías desde el ESP8266

    // Preparar y vincular
    $stmt = $conn->prepare("INSERT INTO datos (valor) VALUES (?)");
    $stmt->bind_param("s", $valor);

    // Ejecutar
    if ($stmt->execute()) {
        echo "<script>alert('Nuevo registro creado exitosamente');</script>";
    } else {
        echo "<script>alert('Error: " . $stmt->error . "');</script>";
    }

    // Cerrar declaración
    $stmt->close();
}

// Obtener todos los registros
$result = $conn->query("SELECT * FROM datos");
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registro de Datos</title>
    <style>
        table {
            width: 50%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h1>Enviar Datos al ESP8266</h1>
    <form method="POST">
        <label for="data">Valor:</label>
        <input type="text" id="data" name="data" required>
        <input type="submit" value="Enviar">
    </form>

    <h2>Registros en la Base de Datos</h2>
    <table>
        <tr>
            <th>ID</th>
            <th>Valor</th>
        </tr>
        <?php
        if ($result->num_rows > 0) {
            // Mostrar cada registro
            while ($row = $result->fetch_assoc()) {
                echo "<tr><td>" . $row["id"] . "</td><td>" . $row["valor"] . "</td></tr>";
            }
        } else {
            echo "<tr><td colspan='2'>No hay registros</td></tr>";
        }
        ?>
    </table>
</body>
</html>

<?php
// Import the functions you need from the SDKs you need
// import { initializeApp } from "firebase/app";
// import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
// const firebaseConfig = {
//   apiKey: "AIzaSyA_wlYn9Y-4qmdimgrZd2tzDtYak8pOpz4",
//   authDomain: "sistema-seguridad-647de.firebaseapp.com",
//   projectId: "sistema-seguridad-647de",
//   storageBucket: "sistema-seguridad-647de.appspot.com",
//   messagingSenderId: "624221842731",
//   appId: "1:624221842731:web:e88dc0bdc6fac656e0e96e",
//   measurementId: "G-VJ9LSPRRTW"
// };

// Initialize Firebase
// const app = initializeApp(firebaseConfig);
// const analytics = getAnalytics(app);

// Cerrar conexión

$conn->close();
?>
