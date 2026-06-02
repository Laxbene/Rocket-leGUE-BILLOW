import streamlit as st

st.set_page_config(
    page_title="2D Rocket League Arena",
    page_icon="⚽",
    layout="centered"
)

st.title("⚽ 2D Rocket League - Arena Edition")
st.write("Sammle Boost von den Pads und tippe die Vorwärts-Taste doppelt, um den Boost zu zünden!")

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

// Spielstand
let scoreBlue = 0;
let scoreOrange = 0;

// Tastatur-State & Doppeltipp-Logik
const keys = {};
const lastTap = { w: 0, arrowup: 0 };

window.addEventListener("keydown", e => { 
    const key = e.key.toLowerCase();
    
    // Doppeltipp-Erkennung für Boost
    if (key === "w" && !keys["w"]) {
        let now = Date.now();
        if (now - lastTap.w < 250) p1.activateBoost();
        lastTap.w = now;
    }
    if (e.code === "ArrowUp" && !keys["arrowup"]) {
        let now = Date.now();
        if (now - lastTap.arrowup < 250) p2.activateBoost();
        lastTap.arrowup = now;
    }

    keys[key] = true; 
    keys[e.code] = true; 
    
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
        
        // Geschwindigkeit verlangsamt für bessere Kontrolle
        this.baseMaxSpeed = 2.2;
        this.maxSpeed = this.baseMaxSpeed;
        this.accel = 0.06;
        this.friction = 0.94;
        
        this.width = 26;
        this.height = 16;
        
        // Boost-System
        this.boostAmount = 34; // Startwert
        this.isBoosting = false;
        this.boostTimer = 0;
    }

    activateBoost() {
        if (this.boostAmount >= 15 && !this.isBoosting) {
            this.isBoosting = true;
            this.boostTimer = 45; // Frames, die der Boost anhält
            this.boostAmount -= 20;
        }
    }

    update(forwardKey, backKey, leftKey, rightKey) {
        // Boost-Verhalten regeln
        if (this.isBoosting) {
            this.maxSpeed = this.baseMaxSpeed * 1.8;
            this.speed += this.accel * 2.5;
            this.boostTimer--;
            if (this.boostTimer <= 0) {
                this.isBoosting = false;
            }
        } else {
            this.maxSpeed = this.baseMaxSpeed;
        }

        if (keys[forwardKey]) this.speed += this.accel;
        else if (keys[backKey]) this.speed -= this.accel;
        else if (!this.isBoosting) this.speed *= this.friction;

        if (this.speed > this.maxSpeed) this.speed = this.maxSpeed;
        if (this.speed < -this.maxSpeed/2) this.speed = -this.maxSpeed/2;

        if (keys[leftKey]) this.angle -= 0.035;
        if (keys[rightKey]) this.angle += 0.035;

        this.vx = Math.cos(this.angle) * this.speed;
        this.vy = Math.sin(this.angle) * this.speed;
        this.x += this.vx;
        this.y += this.vy;

        if (this.x < 60) this.x = 60; if (this.x > 640) this.x = 640;
        if (this.y < 80) this.y = 80; if (this.y > 820) this.y = 820;
    }

    draw() {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);
        
        // Boost-Effekt (Feuer-Spur zeichnen)
        if (this.isBoosting) {
            ctx.fillStyle = "#ff6600";
            ctx.fillRect(-this.width/2 - 15, -6, 15, 12);
            ctx.fillStyle = "#ffcc00";
            ctx.fillRect(-this.width/2 - 8, -3, 8, 6);
        }

        ctx.fillStyle = this.color;
        ctx.fillRect(-this.width/2, -this.height/2, this.width, this.height);
        ctx.fillStyle = "#fff"; 
        ctx.fillRect(this.width/2 - 3, -this.height/2, 3, 3);
        ctx.fillRect(this.width/2 - 3, this.height/2 - 3, 3, 3);
        ctx.restore();
    }
}

const p1 = new Car(350, 650, -Math.PI/2, "#3498db"); // Blau
const p2 = new Car(350, 250, Math.PI/2, "#e67e22");  // Orange

// Boost Pads mit Respawn-Zähler
const boostPads = [
    {x: 75, y: 110, type: 'big', active: true, timer: 0}, {x: 625, y: 110, type: 'big', active: true, timer: 0},
    {x: 65, y: 450, type: 'big', active: true, timer: 0}, {x: 635, y: 450, type: 'big', active: true, timer: 0},
    {x: 75, y: 790, type: 'big', active: true, timer: 0}, {x: 625, y: 790, type: 'big', active: true, timer: 0},

    {x: 260, y: 450, type: 'small', active: true, timer: 0}, {x: 440, y: 450, type: 'small', active: true, timer: 0},
    {x: 350, y: 250, type: 'small', active: true, timer: 0}, {x: 350, y: 350, type: 'small', active: true, timer: 0},
    {x: 350, y: 550, type: 'small', active: true, timer: 0}, {x: 350, y: 650, type: 'small', active: true, timer: 0},
    {x: 210, y: 110, type: 'small', active: true, timer: 0}, {x: 490, y: 110, type: 'small', active: true, timer: 0},
    {x: 275, y: 180, type: 'small', active: true, timer: 0}, {x: 425, y: 180, type: 'small', active: true, timer: 0},
    {x: 210, y: 320, type: 'small', active: true, timer: 0}, {x: 490, y: 320, type: 'small', active: true, timer: 0},
    {x: 190, y: 420, type: 'small', active: true, timer: 0}, {x: 510, y: 420, type: 'small', active: true, timer: 0},
    {x: 80, y: 320, type: 'small', active: true, timer: 0},  {x: 620, y: 320, type: 'small', active: true, timer: 0},
    {x: 210, y: 790, type: 'small', active: true, timer: 0}, {x: 490, y: 790, type: 'small', active: true, timer: 0},
    {x: 275, y: 720, type: 'small', active: true, timer: 0}, {x: 425, y: 720, type: 'small', active: true, timer: 0},
    {x: 210, y: 580, type: 'small', active: true, timer: 0}, {x: 490, y: 580, type: 'small', active: true, timer: 0},
    {x: 190, y: 480, type: 'small', active: true, timer: 0}, {x: 510, y: 480, type: 'small', active: true, timer: 0},
    {x: 80, y: 580, type: 'small', active: true, timer: 0},  {x: 620, y: 580, type: 'small', active: true, timer: 0}
];

const arenaLines = [
    {x1: 180, y1: 70, x2: 520, y2: 70},   
    {x1: 520, y1: 70, x2: 640, y2: 190},  
    {x1: 640, y1: 190, x2: 640, y2: 710}, 
    {x1: 640, y1: 710, x2: 520, y2: 830}, 
    {x1: 520, y1: 830, x2: 180, y2: 830}, 
    {x1: 180, y1: 830, x2: 60, y2: 710},  
    {x1: 60, y1: 710, x2: 60, y2: 190},   
    {x1: 60, y1: 190, x2: 180, y2: 70}    
];

function handleWallCollision(ball, line) {
    let dx = line.x2 - line.x1;
    let dy = line.y2 - line.y1;
    let len = Math.sqrt(dx*dx + dy*dy);
    let nx = -dy / len; 
    let ny = dx / len;

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
        ball.x = closestX + nx * ball.radius * (cx * nx + cy * ny > 0 ? 1 : -1);
        ball.y = closestY + ny * ball.radius * (cx * nx + cy * ny > 0 ? 1 : -1);

        let dotProduct = ball.vx * nx + ball.vy * ny;
        ball.vx = ball.vx - 2 * dotProduct * nx;
        ball.vy = ball.vy - 2 * dotProduct * ny;
        ball.vx *= 0.85; 
        ball.vy *= 0.85;
    }
}

function checkCarBallCollision(car, ball) {
    let dx = ball.x - car.x;
    let dy = ball.y - car.y;
    let distance = Math.sqrt(dx * dx + dy * dy);
    if (distance < ball.radius + car.width/2) {
        let angle = Math.atan2(dy, dx);
        // Stärke des Stoßes hängt vom aktuellen Tempo ab
        let force = Math.abs(car.speed) * 1.2 + 1.5;
        ball.vx = Math.cos(angle) * force;
        ball.vy = Math.sin(angle) * force;
    }
}

function checkBoostPads(car) {
    boostPads.forEach(pad => {
        if (!pad.active) {
            pad.timer--;
            if (pad.timer <= 0) pad.active = true;
            return;
        }
        let dx = car.x - pad.x;
        let dy = car.y - pad.y;
        let dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < 20) {
            pad.active = false;
            if (pad.type === 'big') {
                car.boostAmount = Math.min(100, car.boostAmount + 50);
                pad.timer = 400; // Längerer Respawn für große Pads
            } else {
                car.boostAmount = Math.min(100, car.boostAmount + 15);
                pad.timer = 200; // Schnellerer Respawn für kleine Pads
            }
        }
    });
}

function resetField() {
    ball.x = 350; ball.y = 450; ball.vx = 0; ball.vy = 0;
    p1.x = 350; p1.y = 650; p1.angle = -Math.PI/2; p1.speed = 0; p1.isBoosting = false;
    p2.x = 350; p2.y = 250; p2.angle = Math.PI/2; p2.speed = 0; p2.isBoosting = false;
}

function loop() {
    p1.update("w", "s", "a", "d");
    p2.update("arrowup", "arrowdown", "arrowleft", "arrowright");

    ball.x += ball.vx;
    ball.y += ball.vy;
    ball.vx *= 0.99; // Verlangsamte Ballreibung
    ball.vy *= 0.99;

    checkCarBallCollision(p1, ball);
    checkCarBallCollision(p2, ball);

    checkBoostPads(p1);
    checkBoostPads(p2);

    // --- TORE-SCHIESSEN LOGIK ---
    // Orange Tor oben (Y < 70)
    if (ball.y < 70 && ball.x > 270 && ball.x < 430) {
        if (ball.y <= 45) { 
            scoreBlue++; // Tor für Blau
            resetField(); 
        }
        if (ball.x - ball.radius < 270 || ball.x + ball.radius > 430) ball.vx *= -1;
    } 
    // Blau Tor unten (Y > 830)
    else if (ball.y > 830 && ball.x > 270 && ball.x < 430) {
        if (ball.y >= 855) { 
            scoreOrange++; // Tor für Orange
            resetField(); 
        }
        if (ball.x - ball.radius < 270 || ball.x + ball.radius > 430) ball.vx *= -1;
    } 
    else {
        arenaLines.forEach(line => handleWallCollision(ball, line));
    }

    // --- ZEICHNEN ---
    ctx.clearRect(0, 0, 700, 900);

    // Rasen-Struktur
    for(let i=0; i<10; i++) {
        ctx.fillStyle = i % 2 === 0 ? "#143a22" : "#11331c";
        ctx.fillRect(0, 70 + i*76, 700, 76);
    }

    // Pads zeichnen
    boostPads.forEach(pad => {
        if (!pad.active) return;
        ctx.beginPath();
        ctx.arc(pad.x, pad.y, pad.type === 'big' ? 10 : 4, 0, Math.PI*2);
        ctx.fillStyle = pad.type === 'big' ? "#ffcc00" : "#00ff66";
        ctx.fill();
    });

    // Spielfeldlinien
    ctx.strokeStyle = "rgba(255,255,255,0.15)";
    ctx.lineWidth = 4;
    ctx.beginPath(); ctx.arc(350, 450, 80, 0, Math.PI*2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(60, 450); ctx.lineTo(640, 450); ctx.stroke();

    // Tore zeichnen
    ctx.lineWidth = 6;
    ctx.strokeStyle = "#e67e22"; ctx.strokeRect(270, 20, 160, 50); // Oben
    ctx.strokeStyle = "#3498db"; ctx.strokeRect(270, 830, 160, 50); // Unten

    // Arena-Bande
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(arenaLines[0].x1, arenaLines[0].y1);
    arenaLines.forEach(line => ctx.lineTo(line.x2, line.y2));
    ctx.closePath();
    ctx.stroke();

    // Spieler & Ball zeichnen
    p1.draw();
    p2.draw();

    ctx.fillStyle = "#ffffff";
    ctx.beginPath(); ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = "#000"; ctx.lineWidth = 2; ctx.stroke();

    // --- UI OVERLAY (SCORE & BOOST) ---
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 28px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(`${scoreOrange} : ${scoreBlue}`, 350, 460); // Spielstand in der Mitte

    // Boost-Balken anzeigen
    ctx.font = "14px sans-serif";
    ctx.textAlign = "left";
    ctx.fillStyle = "#3498db";
    ctx.fillText(`Boost: ${Math.floor(p1.boostAmount)}%`, 30, 880);
    
    ctx.textAlign = "right";
    ctx.fillStyle = "#e67e22";
    ctx.fillText(`Boost: ${Math.floor(p2.boostAmount)}%`, 670, 40);

    requestAnimationFrame(loop);
}

resetField();
loop();
</script>
</body>
</html>
"""

st.components.v1.html(game_html, height=920, width=720)
