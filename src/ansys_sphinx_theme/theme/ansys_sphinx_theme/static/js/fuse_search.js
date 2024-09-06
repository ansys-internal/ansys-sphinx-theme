require.config({
  paths: {
    fuse: "https://cdn.jsdelivr.net/npm/fuse.js@6.4.6/dist/fuse.min",
  },
});

require(["fuse"], function (Fuse) {
  let fuseInstance;
  let searchData = [];

  function initializeFuse(data) {
    const fuseOptions = {
      keys: ["title", "text"],
      threshold: "{{ threshold }}",
      shouldSort: "{{ should_sort }}",
      useExtendedSearch: "{{ use_extended_search }}",
      ignoreLocation: "{{ ignoreLocation }}",
    };

    fuseInstance = new Fuse(data, fuseOptions);
    searchData = data; // Save the search data for later use
  }

  function performSearch(query) {
    const results = fuseInstance.search(query, {
      limit: parseInt("{{ limit }}"),
    });
    const resultsContainer = document.getElementById("results");
    resultsContainer.innerHTML = "";

    if (results.length === 0) {
      const noResultsMessage = document.createElement("div");
      noResultsMessage.className = "no-results";
      noResultsMessage.textContent = "No matched documents";
      resultsContainer.appendChild(noResultsMessage);
      return; // Exit the function early
    }

    //if query is empty,  dont show the div result container
    if (query === "") {
      resultsContainer.style.display = "none";
      return;
    } else {
      resultsContainer.style.display = "block";
    }

    results.forEach((result) => {
      const item = document.createElement("div");
      item.className = "result-item";
      const { title, text, href } = result.item;

      const highlightedText = highlightTerms(text, query);
      const highlightedTitle = highlightTerms(title, query);

      item.innerHTML =
        `<div class="result-title">${highlightedTitle}</div>` +
        `<div class="result-text">${highlightedText}</div>`;
      item.setAttribute("data-href", href); // Add href data attribute

      // Add click event listener to navigate to the URL
      item.addEventListener("click", () => {
        navigateToHref(href);
      });

      resultsContainer.appendChild(item);
    });
  }

  function stripText(text, query) {
    // get only the sentences that contain the query
    return text
      .replace(/<[^>]*>?/gm, "")
      .split(".")
      .filter((sentence) => sentence.includes(query))
      .join(". ");
  }

  function highlightTerms(text, query) {
    if (!query.trim()) return text;

    // Split query into words and escape special characters for each word
    const words = query.trim().split(/\s+/);
    const escapedWords = words.map((word) =>
      word.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&"),
    );

    // Create a regex to match any of the words
    const regex = new RegExp(`(${escapedWords.join("|")})`, "gi");

    // Replace matched text with highlighted version
    return text.replace(regex, '<span class="highlight">$1</span>');
  }

  function navigateToHref(href) {
    const baseUrl = window.location.origin;
    const relativeUrl = href.startsWith("/") ? href : `/${href}`;
    window.location.href = new URL(relativeUrl, baseUrl).href;
  }

  // Set up the search box event listener
  const searchBox = document.querySelector(".bd-search input");
  searchBox.addEventListener("input", function () {
    const query = this.value.trim();
    performSearch(query);
  });

  // Add event listener for Enter key press
  searchBox.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      const firstResult = document.querySelector(".result-item");
      if (firstResult) {
        // Navigate to the first result's URL
        navigateToHref(firstResult.getAttribute("data-href"));
        // window.location.href = firstResult.getAttribute('data-href');
      }
      event.preventDefault(); // Prevent the default form submission
    }
  });

  // Fetch the data from search.json and initialize Fuse.js
  fetch('{{ pathto("search.json", 1) }}')
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok " + response.statusText);
      }
      return response.json();
    })
    .then((data) => {
      initializeFuse(data);
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
    });
});
