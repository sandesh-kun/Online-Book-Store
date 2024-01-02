// Get the clock element
const clock = document.getElementById('clock');

// Update the clock every second
function updateClock() {
  const now = new Date();
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const seconds = now.getSeconds().toString().padStart(2, '0');
  clock.textContent = `${hours}:${minutes}:${seconds}`;
}

// Update the clock immediately and then every second
updateClock();
setInterval(updateClock, 1000);
