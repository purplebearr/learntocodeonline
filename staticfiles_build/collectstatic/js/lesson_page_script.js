
  const csrfToken = "{{ csrf_token }}"; // Get the CSRF token from the context
  const lessonIdJson = "{{ lesson_id_json|escapejs }}"; // Get the lesson ID from the context
  const userIdJson = "{{ user_id_json|escapejs }}"; // Get the user ID from the context

  const lessonId = JSON.parse(lessonIdJson);
  const userId = JSON.parse(userIdJson);

  let typingTimer;

  function handleTyping() {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(saveCodeToServer, 3000);
    console.log("safv");
  }

  function saveCodeToServer() {
    const code = editor.getValue(); // Replace 'repl.getPySrc()' with 'editor.getValue();

    const data = {
      user: userId,
      lesson: lessonId,
      saved_compiler_code: code,
    };

    fetch("{% url 'save_code' %}", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(data),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to save code");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }