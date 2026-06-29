document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('cropForm');
    const resultSection = document.getElementById('prediction-result-section');
    const resultCrop = document.getElementById('result-crop');
    const resultConfidence = document.getElementById('result-confidence');
    const resultDescription = document.getElementById('result-description');
    const resultNpk = document.getElementById('result-npk');
    const resultTempHumidity = document.getElementById('result-temphumidity');
    const resultPhRainfall = document.getElementById('result-phrainfall');
    const predictBtn = document.querySelector('.predict-btn');

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Clear previous errors
            document.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');

            // Get form values
            const n = document.getElementById('N').value;
            const p = document.getElementById('P').value;
            const k = document.getElementById('K').value;
            const temperature = document.getElementById('temperature').value;
            const humidity = document.getElementById('humidity').value;
            const ph = document.getElementById('ph').value;
            const rainfall = document.getElementById('rainfall').value;

            // Simple loading state
            const originalBtnText = predictBtn.innerHTML;
            predictBtn.disabled = true;
            predictBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Predicting...';

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        N: n,
                        P: p,
                        K: k,
                        temperature: temperature,
                        humidity: humidity,
                        ph: ph,
                        rainfall: rainfall
                    })
                });

                const data = await response.json();

                if (response.ok && data.status === 'success') {
                    // Update result section
                    const crop = data.prediction;
                    // Capitalize crop name
                    const capitalizedCrop = crop.charAt(0).toUpperCase() + crop.slice(1);
                    resultCrop.textContent = capitalizedCrop;

                    // Get confidence from probabilities if available
                    let confidenceText = '';
                    if (data.probabilities) {
                        const confidence = data.probabilities[crop] || 0;
                        confidenceText = `Confidence : ${(confidence * 100).toFixed(2)}%`;
                    }
                    resultConfidence.textContent = confidenceText;

                    // Set description
                    resultDescription.innerHTML = `<strong>${capitalizedCrop}</strong> is the most suitable crop based on the soil nutrients, rainfall, humidity and temperature provided.`;

                    // Set details
                    resultNpk.textContent = `${n} - ${p} - ${k}`;
                    resultTempHumidity.textContent = `${temperature}°C / ${humidity}%`;
                    resultPhRainfall.textContent = `${ph} / ${rainfall}mm`;

                    // Show result section
                    resultSection.classList.remove('d-none');

                    // Scroll to result section
                    resultSection.scrollIntoView({ behavior: 'smooth' });
                } else {
                    // Handle failure or validation errors
                    if (data.errors) {
                        for (const [key, msg] of Object.entries(data.errors)) {
                            const errorEl = document.getElementById(`error-${key}`);
                            if (errorEl) {
                                errorEl.textContent = msg;
                            }
                        }
                    } else if (data.message) {
                        alert(`Error: ${data.message}`);
                    } else {
                        alert('An unexpected error occurred during prediction.');
                    }
                }
            } catch (err) {
                console.error(err);
                alert('Connection error. Please try again.');
            } finally {
                predictBtn.disabled = false;
                predictBtn.innerHTML = originalBtnText;
            }
        });
    }
});
