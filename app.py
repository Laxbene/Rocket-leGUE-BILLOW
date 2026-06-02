import streamlit as st

st.set_page_config(
    page_title="2D Rocket League Arena",
    page_icon="⚽",
    layout="centered"
)

st.title("⚽ 2D Rocket League - Arena Edition")
st.write("Fahre über die Pads, um Energie aufzuladen (Zukunft) und schieße Tore in der echten Arena!")

# Spielfeld als HTML5 Canvas + JavaScript
game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; display: flex; justify-content: center; align-items: center; background: #111; overflow: hidden; }
        canvas { background: #14351f; box-shadow: 0 0 30px rgba(0,0,0,0.7); }
    </style>
</head>
<body>

<canvas id="gameCanvas" width="700" height="900"></canvas>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Tastatur-State & Scroll-Blocker
const keys = {};
window.addEventListener("keydown", e => { 
    keys[e.key.toLowerCase()] = true; 
    keys[e.code] = true; 
    // Verhindert das Scrollen bei Pfeiltasten und Leertaste
    if(["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Space"].includes(e.code)) {
        e.preventDefault();
    }
}, { passive: false });

window.addEventListener("keyup", e => { 
    keys[e.key.toLowerCase()] = false; 
    keys[e.code] = false; 
});

// Spielobjekte
const ball = { x: 350, y: 450, vx: 0, vy: 0, radius: 14 };

class Car {
    constructor(x, y, angle, color) {
        this.x = x;
        this.y = y;
        this.vx = 0;
        this.vy = 0;
        this.angle = angle;
        this.color = color;
        this.speed = 0;
        this.maxSpeed = 4.5;
        this.accel = 0.12;
        this.friction = 0.96;
        this.width = 26;
        this.height = 16;
    }

    update(forwardKey, backKey, leftKey, rightKey) {
        if (keys[forwardKey]) this.speed += this.accel;
        else if (keys[backKey]) this.speed -= this.accel;
        else this.speed *= this.friction;

        if (this.speed > this.maxSpeed) this.speed = this.maxSpeed;
        if (this.speed < -this.maxSpeed/2) this.speed = -this.maxSpeed/2;

        if (keys[leftKey]) this.angle -= 0.045;
        if (keys[rightKey]) this.angle += 0.045;

        this.vx = Math.cos(this.angle) * this.speed;
        this.vy = Math.sin(this.angle) * this.speed;
        this.x += this.vx;
        this.y += this.vy;

        // Auto-Kollision mit Außenwand (vereinfacht für Arena-Box)
        if (this.x < 60) this.x = 60; if (this.x > 640) this.x = 640;
        if (this.y < 80) this.y = 80; if (this.y > 820) this.y = 820;
    }

    draw() {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);
        ctx.fillStyle = this.color;
        ctx.fillRect(-this.width/2, -this.height/2, this.width, this.height);
        ctx.fillStyle = "#fff"; // Scheinwerfer
        ctx.fillRect(this.width/2 - 3, -this.height/2, 3, 3);
        ctx.fillRect(this.width/2 - 3, this.height/2 - 3, 3, 3);
        ctx.restore();
    }
}

const p1 = new Car(350, 650, -Math.PI/2, "#3498db"); // Blau (unten)
const p2 = new Car(350, 250, Math.PI/2, "#e67e22");  // Orange (oben)

// Boost Pads Koordinaten exakt nach deinem Bild generiert
const boostPads = [
    // 100er Große Boosts (Gelb)
    {x: 75, y: 110, type: 'big'}, {x: 625, y: 110, type: 'big'},
    {x: 65, y: 450, type: 'big'}, {x: 635, y: 450, type: 'big'},
    {x: 75, y: 790, type: 'big'}, {x: 625, y: 790, type: 'big'},

    // 12er Kleine Boosts (Grün) - Mittellinie & Kreise nachgebaut
    {x: 260, y: 450, type: 'small'}, {x: 440, y: 450, type: 'small'},
    {x: 350, y: 250, type: 'small'}, {x: 350, y: 350, type: 'small'},
    {x: 350, y: 550, type: 'small'}, {x: 350, y: 650, type: 'small'},
    // Obere Hälfte
    {x: 210, y: 110, type: 'small'}, {x: 490, y: 110, type: 'small'},
    {x: 275, y: 180, type: 'small'}, {x: 425, y: 180, type: 'small'},
    {x: 210, y: 320, type: 'small'}, {x: 490, y: 320, type: 'small'},
    {x: 190, y: 420, type: 'small'}, {x: 510, y: 420, type: 'small'},
    {x: 80, y: 320, type: 'small'},  {x: 620, y: 320, type: 'small'},
    // Untere Hälfte
    {x: 210, y: 790, type: 'small'}, {x: 490, y: 790, type: 'small'},
    {x: 275, y: 720, type: 'small'}, {x: 425, y: 720, type: 'small'},
    {x: 210, y: 580, type: 'small'}, {x: 490, y: 580, type: 'small'},
    {x: 190, y: 480, type: 'small'}, {x: 510, y: 480, type: 'small'},
    {x: 80, y: 580, type: 'small'},  {x: 620, y: 580, type: 'small'}
];

// Definition der Arena-Wände (Achteck)
const arenaLines = [
    {x1: 180, y1: 70, x2: 520, y2: 70},   // Oben (Torwand Orange)
    {x1: 520, y1: 70, x2: 640, y2: 190},  // Ecke oben rechts
    {x1: 640, y1: 190, x2: 640, y2: 710}, // Rechts
    {x1: 640, y1: 710, x2: 520, y2: 830}, // Ecke unten rechts
    {x1: 520, y1: 830, x2: 180, y2: 830}, // Unten (Torwand Blau)
    {x1: 180, y1: 830, x2: 60, y2: 710},  // Ecke unten links
    {x1: 60, y1: 710, x2: 60, y2: 190},   // Links
    {x1: 60, y1: 190, x2: 180, y2: 70}    // Ecke oben links
];

function handleWallCollision(ball, line) {
    let dx = line.x2 - line.x1;
    let dy = line.y2 - line.y1;
    let len = Math.sqrt(dx*dx + dy*dy);
    let nx = -dy / len; // Normalenvektor
    let ny = dx / len;

    // Distanz von Ball zu Linie
    let cx = ball.x - line.x1;
    let cy = ball.y - line.y1;
    let dot = (cx * dx + cy * dy) / (len * len);
    dot = Math.max(0, Math.min(1, dot));
    
    let closestX = line.x1 + dot * dx;
    let closestY = line.y1 + dot * dy;
    
    let distDX = ball.x - closestX;
    let distDY = ball.y - closestY;
    let dist = Math.sqrt(distDX*distDX + distDY*distDY);

    if (dist < ball.radius) {
        // Drücke Ball aus der Wand heraus
        ball.x = closestX + nx * ball.radius * (cx * nx + cy * ny > 0 ? 1 : -1);
        ball.y = closestY + ny * ball.radius * (cx * nx + cy * ny > 0 ? 1 : -1);

        // Reflektiere Vektor
        let dotProduct = ball.vx * nx + ball.vy * ny;
        ball.vx = ball.vx - 2 * dotProduct * nx;
        ball.vy = ball.vy - 2 * dotProduct * ny;
        ball.vx *= 0.9; // Energieverlust beim Aufprall
        ball.vy *= 0.9;
    }
}

function checkCarBallCollision(car, ball) {
    let dx = ball.x - car.x;
    let dy = ball.y - car.y;
    let distance = Math.sqrt(dx * dx + dy * dy);
    if (distance < ball.radius + car.width/2) {
        let angle = Math.atan2(dy, dx);
        let force = Math.abs(car.speed) + 2.5;
        ball.vx = Math.cos(angle) * force;
        ball.vy = Math.sin(angle) * force;
    }
}

function resetField() {
    ball.x = 350; ball.y = 450; ball.vx = 0; ball.vy = 0;
    p1.x = 350; p1.y = 650; p1.angle = -Math.PI/2; p1.speed = 0;
    p2.x = 350; p2.y = 250; p2.angle = Math.PI/2; p2.speed = 0;
}

function loop() {
    p1.update("w", "s", "a", "d");
    p2.update("arrowup", "arrowdown", "arrowleft", "arrowright");

    ball.x += ball.vx;
    ball.y += ball.vy;
    ball.vx *= 0.985;
    ball.vy *= 0.985;

    checkCarBallCollision(p1, ball);
    checkCarBallCollision(p2, ball);

    // Tor-Logik (Tore sind zwischen X: 270 und 430 außerhalb der Wand)
    if (ball.y < 70 && ball.x > 270 && ball.x < 430) {
        if (ball.y < 25) { alert("TOR FÜR BLAU!"); resetField(); }
        // Seitliche Pfosten im Tor
        if (ball.x - ball.radius < 270 || ball.x + ball.radius > 430) ball.vx *= -1;
        if (ball.y - ball.radius < 20) ball.vy *= -1;
    } else if (ball.y > 830 && ball.x > 270 && ball.x < 430) {
        if (ball.y > 875) { alert("TOR FÜR ORANGE!"); resetField(); }
        if (ball.x - ball.radius < 270 || ball.x + ball.radius > 430) ball.vx *= -1;
        if (ball.y + ball.radius > 880) ball.vy *= -1;
    } else {
        // Normale Bandenkollision, wenn nicht im Torraum
        arenaLines.forEach(line => handleWallCollision(ball, line));
    }

    // --- ZEICHNEN ---
    ctx.clearRect(0, 0, 700, 900);

    // Rasen-Struktur (Streifen)
    for(let i=0; i<10; i++) {
        ctx.fillStyle = i % 2 === 0 ? "#143a22" : "#11331c";
        ctx.fillRect(0, 70 + i*76, 700, 76);
    }

    // Boost Pads zeichnen
    boostPads.forEach(pad => {
        ctx.beginPath();
        ctx.arc(pad.x, pad.y, pad.type === 'big' ? 12 : 5, 0, Math.PI*2);
        ctx.fillStyle = pad.type === 'big' ? "#ffcc00" : "#00ff66";
        ctx.shadowColor = ctx.fillStyle;
        ctx.shadowBlur = 10;
        ctx.fill();
        ctx.shadowBlur = 0; // Reset
    });

    // Mittelkreis & Linien
    ctx.strokeStyle = "rgba(255,255,255,0.2)";
    ctx.lineWidth = 4;
    ctx.beginPath(); ctx.arc(350, 450, 80, 0, Math.PI*2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(60, 450); ctx.lineTo(640, 450); ctx.stroke();

    // Echte herausstehende Tore zeichnen
    ctx.lineWidth = 6;
    // Orange Tor (Oben)
    ctx.strokeStyle = "#e67e22";
    ctx.strokeRect(270, 20, 160, 50);
    // Blau Tor (Unten)
    ctx.strokeStyle = "#3498db";
    ctx.strokeRect(270, 830, 160, 50);

    // Arena-Bande zeichnen (Leuchtendes Weiß/Grau)
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 5;
    ctx.shadowColor = "#ffffff";
    ctx.shadowBlur = 5;
    ctx.beginPath();
    ctx.moveTo(arenaLines[0].x1, arenaLines[0].y1);
    arenaLines.forEach(line => ctx.lineTo(line.x2, line.y2));
    ctx.closePath();
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Spieler & Ball
    p1.draw();
    p2.draw();

    // Ball zeichnen
    ctx.fillStyle = "#ffffff";
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#000";
    ctx.lineWidth = 2;
    ctx.stroke();

    requestAnimationFrame(loop);
}

resetField();
loop();
</script>
</body>
</html>
"""

st.components.v1.html(game_html, height=920, width=720)
st.info("ℹ️ Klicke einmal kurz auf das Spielfeld. Die Pfeiltasten bewegen jetzt NUR das Auto, die Webseite bleibt fest verankert!")
