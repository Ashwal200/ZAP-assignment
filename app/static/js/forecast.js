/* global Chart */

document.addEventListener("DOMContentLoaded", () => {
  const openBtn  = document.getElementById("alertBtn");
  const popup    = document.getElementById("resultPopup");
  const closeBtn = document.getElementById("closePopup");
  const ctx      = document.getElementById("forecastChart").getContext("2d");
  let chart;

  // Utility to safely destroy previous chart instance
  const destroyChart = () => {
    if (chart) {
      chart.destroy();
      chart = null;
    }
  };

  // Main routine: fetch forecast, compute insight, and draw chart
  const drawForecast = async () => {
    const data   = await fetch("/forecast_next_week").then(r => r.json());
    const labels = data.map(r => r.date);
    const values = data.map(r => r.price);
    const minIdx = values.indexOf(Math.min(...values));
    const maxIdx = values.indexOf(Math.max(...values));

    // ─── Insight Message Logic ───────────────────────────────
    const highestPrice = values[maxIdx];
    const lowestPrice = values[minIdx];
    const dropPercent = ((highestPrice - lowestPrice) / highestPrice) * 100;
    const dayGap = Math.abs(minIdx - maxIdx);

    const insightBox = document.getElementById("priceInsight");
    if (insightBox) {
      let message = "";
      // Simple heuristic: if a higher price appears before a lower one, suggest waiting
      if (dropPercent >= 0 && maxIdx < minIdx) {
        message = `Wait, expected to drop ${dropPercent.toFixed(1)}% in ${dayGap} day${dayGap > 1 ? "s" : ""}`;
      } else {
        message = "Buy now, price unlikely to improve";
      }
      insightBox.textContent = message;
    }

    // Draw Chart 
    destroyChart();

    chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Predicted Price',
          data: values,
          borderColor: '#28a745',
          fill: false,
          tension: 0.2,
          pointRadius: values.map((_, i) => (i === minIdx || i === maxIdx) ? 8 : 4),
          pointBackgroundColor: values.map((_, i) =>
            i === minIdx ? 'blue' :
            i === maxIdx ? 'red' : '#28a745'
          )
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { title: { display: true, text: 'Date' } },
          y: {
            title: { display: true, text: 'Price (₪)' },
            ticks: { callback: v => `₪${v}` }
          }
        },
        plugins: { legend: { display: false } }
      }
    });
  };

  // Open forecast popup and initiate forecast drawing
  openBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    await drawForecast();
    popup.classList.remove("hidden");
  });

  // Close via close button
  closeBtn.addEventListener("click", () => {
    popup.classList.add("hidden");
    destroyChart();
  });

  // Close if clicking outside the content area
  popup.addEventListener("click", (e) => {
    if (e.target === popup) {
      popup.classList.add("hidden");
      destroyChart();
    }
  });

  // Subscription form handler 
  const subscribeBtn = document.getElementById("subscribeBtn");
  subscribeBtn.addEventListener("click", async () => {
    const phone   = document.getElementById("phoneNumber").value.trim();
    const desired = document.getElementById("desiredPrice").value.trim();
    if (!phone || !desired) return alert("Please enter both phone and desired price.");

    // Send subscription request
    const resp = await fetch("/subscribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        phone_number: phone,
        desired_price: desired,
        description: "Samsung UE55DU7100 4K 55 inch TV"
      })
    });

    const result = await resp.json();
    alert(result.message);
    popup.classList.add("hidden");
    destroyChart();
  });
});
