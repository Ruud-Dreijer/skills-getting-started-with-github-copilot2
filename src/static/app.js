document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  function showMessage(message, type) {
    messageDiv.textContent = message;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");

    // Hide message after 5 seconds
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      console.log("Fetching activities...");
      const response = await fetch("/activities");
      const activities = await response.json();
      console.log("Activities received:", activities);

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Create participants list HTML
        const participantsList = details.participants.length > 0 
          ? `<div class="participants-list">${details.participants.map(email => 
              `<div class="participant-item">
                <span class="participant-email">${email}</span>
                <button class="delete-participant" data-activity="${name}" data-email="${email}" title="Remove participant">×</button>
              </div>`
            ).join('')}</div>`
          : '<p class="no-participants">No participants yet</p>';

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <h5>Current Participants:</h5>
            ${participantsList}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add event listeners for delete buttons
        const deleteButtons = activityCard.querySelectorAll('.delete-participant');
        deleteButtons.forEach(button => {
          button.addEventListener('click', async (event) => {
            event.preventDefault();
            const activityName = button.getAttribute('data-activity');
            const email = button.getAttribute('data-email');
            
            if (confirm(`Remove ${email} from ${activityName}?`)) {
              try {
                const response = await fetch(
                  `/activities/${encodeURIComponent(activityName)}/participants/${encodeURIComponent(email)}`,
                  {
                    method: "DELETE",
                  }
                );

                if (response.ok) {
                  console.log("Delete successful, refreshing activities...");
                  // Refresh activities list
                  fetchActivities();
                  showMessage(`Removed ${email} from ${activityName}`, 'success');
                } else {
                  const result = await response.json();
                  showMessage(result.detail || "Failed to remove participant", 'error');
                }
              } catch (error) {
                showMessage("Failed to remove participant. Please try again.", 'error');
                console.error("Error removing participant:", error);
              }
            }
          });
        });
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
      console.log("Activities display updated successfully");
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        console.log("Signup successful, refreshing activities...");
        showMessage(result.message, "success");
        signupForm.reset();
        // Refresh activities to show the new participant
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
