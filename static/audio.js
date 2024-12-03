document.addEventListener('DOMContentLoaded', function() {
    const audioElements = document.querySelectorAll('audio');
    audioElements.forEach((audio, index) => {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioContext.createMediaElementSource(audio);
      const gainNode = audioContext.createGain();
      const bass = audioContext.createBiquadFilter();
      const lowMid = audioContext.createBiquadFilter();
      const mid = audioContext.createBiquadFilter();
      const highMid = audioContext.createBiquadFilter();
      const treble = audioContext.createBiquadFilter();
  
      bass.type = 'lowshelf';
      lowMid.type = 'peaking';
      mid.type = 'peaking';
      highMid.type = 'peaking';
      treble.type = 'highshelf';
  
      bass.frequency.value = 60;
      lowMid.frequency.value = 250;
      mid.frequency.value = 1000;
      highMid.frequency.value = 4000;
      treble.frequency.value = 10000;
  
      source.connect(bass);
      bass.connect(lowMid);
      lowMid.connect(mid);
      mid.connect(highMid);
      highMid.connect(treble);
      treble.connect(gainNode);
      gainNode.connect(audioContext.destination);
  
      document.getElementById(`bass-${index + 1}`).addEventListener('input', function() {
        bass.gain.value = this.value;
      });
  
      document.getElementById(`low-mid-${index + 1}`).addEventListener('input', function() {
        lowMid.gain.value = this.value;
      });
  
      document.getElementById(`mid-${index + 1}`).addEventListener('input', function() {
        mid.gain.value = this.value;
      });
  
      document.getElementById(`high-mid-${index + 1}`).addEventListener('input', function() {
        highMid.gain.value = this.value;
      });
  
      document.getElementById(`treble-${index + 1}`).addEventListener('input', function() {
        treble.gain.value = this.value;
      });
    });
  });
