import streamlit as st

# Seiteneinstellungen
st.set_page_config(
    page_title="2D Rocket League",
    page_icon="⚽",
    layout="centered"
)

st.title("⚽ 2D Rocket League")
st.write("Spielt zusammen an einer Tastatur! Schießt den Ball ins gegnerische Tor.")

# Erklärung der Steuerung
col1, col2 = st.columns(2)
with col1:
    st.subheader("🔵 Spieler 1 (Blau)")
    st.markdown("* **W / S**: Gas / Rückwärts\n* **A / D**: Lenken")
with col2:
    st.subheader("🟠 Spieler 2 (Orange)")
    st.markdown("* **▲ / ▼**: Gas / Rückwärts\n* **◄ / ►**: Lenken")

# Das komplette Spiel als HTML5 Canvas + JavaScript
game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; display: flex; justify-content: center; align-items: center; background: #222; }
        canvas { border: 4px solid #fff; background: #1a472a; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
    </style>
</head>
<body>

<canvas id="gameCanvas" width="800" height="500"></canvas>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Tastatur-State
const keys = {};
window.addEventListener("keydown", e => { keys[e.key.toLowerCase()] = true; keys[e.code] = true; });
window.addEventListener("keyup", e => { keys[e.key.toLowerCase()] = false; keys[e.code] = false; });

// Physik & Spiel-Objekte
const ball = { x: 400, y: 250, vx: 0, vy: 0, radius: 15 };

class Car {
    constructor(x, y, angle, color) {
        self = this;
        this.x = x;
        this.y = y;
        this.vx = 0;
        this.vy = 0;
        this.angle = angle;
        this.color = color;
        this.speed = 0;
        this.maxSpeed = 5;
        this.accel = 0.15;
        this.friction = 0.95;
        this.width = 30;
        this.height = 18;
    }

    update(forwardKey, backKey, leftKey, rightKey) {
        // Gas & Rückwärts
        if (keys[forwardKey]) this.speed += this.accel;
        else if (keys[backKey]) this.speed -= this.accel;
        else this.speed *= this.friction;

        // Speed-Limit
        if (this.speed > this.maxSpeed) this.speed = this.maxSpeed;
        if (this.speed < -this.maxSpeed/2) this.speed = -this.maxSpeed/2;

        // Lenken
        if (keys[leftKey]) this.angle -= 0.05;
        if (keys[rightKey]) this.angle += 0.05;

        // Bewegung berechnen
        this.vx = Math.cos(this.angle) * this.speed;
        this.vy = Math.sin(this.angle) * this.speed;
        this.x += this.vx;
        this.y += this.vy;

        // Banden-Kollision Auto
        if (this.x < 15) this.x = 15;
        if (this.x > 785) this.x = 785;
        if (this.y < 15) this.y = 15;
        if (this.y > 485) this.y = 485;
    }

    draw() {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);
        ctx.fillStyle = this.color;
        // Auto-Körper
        ctx.fillRect(-this.width/2, -this.height/2, this.width, this.height);
        // Scheinwerfer (Vorne)
        ctx.fillStyle = "#fff";
        ctx.fillRect(this.width/2 - 4, -this.height/2, 4, 4);
        ctx.fillRect(this.width/2 - 4, this.height/2 - 4, 4, 4);
        ctx.restore();
    }
}

const p1 = new Car(150, 250, 0, "#3498db"); // Blau
const p2 = new Car(650, 250, Math.PI, "#e67e22"); // Orange

// Tore definieren
const goalYStart = 175;
const goalYEnd = 325;

function checkCollision(car, ball) {
    let dx = ball.x - car.x;
    let dy = ball.y - car.y;
    let distance = Math.sqrt(dx * dx + dy * dy);
    
    if (distance < ball.radius + car.width/2) {
        // Einfacher physikalischer Impuls bei Stoß
        let angle = Math.atan2(dy, dx);
        ball.vx = Math.cos(angle) * (Math.abs(car.speed) + 3);
        ball.vy = Math.sin(angle) * (Math.abs(car.speed) + 3);
    }
}

function resetField() {
    ball.x = 400; ball.y = 250; ball.vx = 0; ball.vy = 0;
    p1.x = 150; p1.y = 250; p1.angle = 0; p1.speed = 0;
    p2.x = 650; p2.y = 250; p2.angle = Math.PI; p2.speed = 0;
}

// Game Loop
function loop() {
    // Updates
    p1.update("w", "s", "a", "d");
    p2.update("arrowup", "arrowdown", "arrowleft", "arrowright");

    // Ball-Physik
    ball.x += ball.vx;
    ball.y += ball.vy;
    ball.vx *= 0.98; // Reibung des Balls
    ball.vy *= 0.98;

    // Kollisionen Auto -> Ball
    checkCollision(p1, ball);
    checkCollision(p2, ball);

    // Wand-Kollisionen Ball
    if (ball.y - ball.radius < 0 || ball.y + ball.radius > 500) ball.vy *= -1;
    
    // Tor-Abfrage oder Wand-Abfrage an den Seiten
    if (ball.x - ball.radius < 0) {
        if (ball.y > goalYStart && ball.y < goalYEnd) {
            alert("TOR FÜR ORANGE!");
            resetField();
        } else {
            ball.vx *= -1;
            ball.x = ball.radius;
        }
    }
    if (ball.x + ball.radius > 800) {
        if (ball.y > goalYStart && ball.y < goalYEnd) {
            alert("TOR FÜR BLAU!");
            resetField();
        } else {
            ball.vx *= -1;
            ball.x = 800 - ball.radius;
        }
    }

    // Zeichnen
    ctx.clearRect(0, 0, 800, 500);

    // Spielfeld-Linien
    ctx.strokeStyle = "rgba(255,255,255,0.3)";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(400, 0); ctx.lineTo(400, 500); // Mittellinie
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(400, 250, 75, 0, Math.PI * 2); // Mittelkreis
    ctx.stroke();

    // Tore zeichnen
    ctx.fillStyle = "#3498db";
    ctx.fillRect(0, goalYStart, 10, goalYEnd - goalYStart);
    ctx.fillStyle = "#e67e22";
    ctx.fillRect(790, goalYStart, 10, goalYEnd - goalYStart);

    // Autos und Ball zeichnen
    p1.draw();
    p2.draw();

    ctx.fillStyle = "#fff";
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#000";
    ctx.stroke();

    requestAnimationFrame(loop);
}

resetField();
loop();
</script>
</body>
</html>
"""

# HTML-Komponente in Streamlit rendern
st.components.v1.html(game_html, height=530, width=820)

st.info("💡 Klicke einmal kurz in das Spielfeld, damit deine Tastaturbefehle registriert werden!")
