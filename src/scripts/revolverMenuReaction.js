const initDrumReaction = () => {
  const sensor = document.querySelector('.menuMouseSensor');
  const drum = document.getElementById('drum');
  if (sensor && drum) {
    sensor.addEventListener('mouseenter', () => {
      drum.style.animationPlayState = 'running';
      drum.style.animationDirection = 'normal';
    });
    sensor.addEventListener('mouseleave', () => {
      // Режим reverse работает, еслиmouse оставили до завершения полного цикла (1с).
      // Если оставили после — будет небольшой "скелет" в начало, но направление будет обратным.
      drum.style.animationDirection = 'reverse';
    });
  }
};

// Ensure the DOM is ready before attaching reactivity
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDrumReaction);
} else {
  initDrumReaction();
}