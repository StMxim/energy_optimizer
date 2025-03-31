document.addEventListener('DOMContentLoaded', function() {
  // Get UI elements
  const marketDataForm = document.getElementById('market-data-form');
  const optimizationForm = document.getElementById('optimization-form');
  const csvUploadForm = document.getElementById('csv-upload-form');
  const resultsTableBody = document.getElementById('results-table-body');
  const resultsSummary = document.getElementById('results-summary');
  const loadingIndicator = document.getElementById('loading');
  const alertContainer = document.getElementById('alert-container');
  const downloadCsvBtn = document.getElementById('download-csv');
  const clearResultsBtn = document.getElementById('clear-results-btn');
  const tabs = document.querySelectorAll('.tabs a');
  
  // Элементы мобильного меню
  const burgerMenu = document.querySelector('.burger-menu');
  const navMenu = document.querySelector('nav');
  const overlay = document.querySelector('.overlay');
  
  // Page initialization
  init();
  
  function init() {
    // Set current date and date one week ago
    setDefaultDates();
    
    // Activate tabs
    activateTabs();
    
    // Add event listeners
    if (marketDataForm) marketDataForm.addEventListener('submit', handleMarketDataSubmit);
    if (optimizationForm) optimizationForm.addEventListener('submit', handleOptimizationSubmit);
    if (csvUploadForm) csvUploadForm.addEventListener('submit', handleCsvUpload);
    if (clearResultsBtn) clearResultsBtn.addEventListener('click', handleClearResults);
    
    // Initialize results container
    const resultsContainer = document.getElementById('results-container');
    if (resultsContainer) {
      resultsContainer.style.display = 'none';
    }
    
    // Enhance date inputs
    enhanceDateInputs();
    
    // Initialize mobile menu
    initMobileMenu();
  }
  
  // Функция для инициализации мобильного меню
  function initMobileMenu() {
    if (!burgerMenu || !navMenu || !overlay) return;
    
    // Переменная для отслеживания состояния меню
    let menuOpen = false;
    
    // Функция для открытия меню
    function openMenu() {
      if (menuOpen) return;
      
      burgerMenu.classList.add('active');
      burgerMenu.setAttribute('aria-expanded', 'true');
      navMenu.classList.add('active');
      overlay.classList.add('active');
      document.body.style.overflow = 'hidden';
      menuOpen = true;
      
      // Добавляем обработчик для закрытия меню по клавише ESC
      document.addEventListener('keydown', handleEscKey);
    }
    
    // Функция для закрытия меню
    function closeMenu() {
      if (!menuOpen) return;
      
      burgerMenu.classList.remove('active');
      burgerMenu.setAttribute('aria-expanded', 'false');
      navMenu.classList.remove('active');
      overlay.classList.remove('active');
      document.body.style.overflow = '';
      menuOpen = false;
      
      // Удаляем обработчик клавиши ESC
      document.removeEventListener('keydown', handleEscKey);
    }
    
    // Функция для обработки клавиши ESC
    function handleEscKey(e) {
      if (e.key === 'Escape') {
        closeMenu();
      }
    }
    
    // Функция для переключения меню
    function toggleMenu(e) {
      e.stopPropagation(); // Предотвращаем всплытие события
      
      if (menuOpen) {
        closeMenu();
      } else {
        openMenu();
      }
    }
    
    // Обработчик клика по бургер-меню с предотвращением событий
    burgerMenu.addEventListener('click', toggleMenu);
    
    // Обработчик клика по оверлею
    overlay.addEventListener('click', closeMenu);
    
    // Закрытие меню при клике на пункт меню - только на мобильных устройствах (< 992px)
    const menuLinks = navMenu.querySelectorAll('a');
    for (const link of menuLinks) {
      link.addEventListener('click', () => {
        // Проверяем, находимся ли мы в мобильном режиме
        if (window.innerWidth <= 992) {
          closeMenu();
        }
      });
    }
    
    // Закрытие меню при ресайзе окна 
    let resizeTimeout;
    window.addEventListener('resize', () => {
      // Используем debounce для предотвращения множественных вызовов
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        if (window.innerWidth > 992 && menuOpen) {
          closeMenu();
        }
      }, 100);
    });
    
    // Запрещаем показ бургер-меню на десктопе
    function updateMenuVisibility() {
      if (window.innerWidth > 992) {
        burgerMenu.style.display = 'none';
        overlay.style.display = 'none';
      } else {
        burgerMenu.style.display = 'flex';
      }
    }
    
    // Вызываем функцию при загрузке и изменении размера окна
    updateMenuVisibility();
    window.addEventListener('resize', updateMenuVisibility);
  }
  
  // Function to enhance date inputs to make them more user-friendly
  function enhanceDateInputs() {
    const dateWrappers = document.querySelectorAll('.date-input-wrapper');
    
    for (const wrapper of dateWrappers) {
      wrapper.addEventListener('click', function(e) {
        // Prevent default to stop any other event handlers
        e.preventDefault();
        
        // Find the input inside the wrapper
        const dateInput = this.querySelector('input[type="date"]');
        
        if (dateInput) {
          // Focus on the input
          dateInput.focus();
          
          // Open the date picker
          dateInput.showPicker();
        }
      });
    }
  }
  
  function setDefaultDates() {
    const today = new Date();
    const lastWeek = new Date();
    lastWeek.setDate(today.getDate() - 7);
    
    // Format dates for date input
    const formatDate = (date) => {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    };
    
    // Set values in date fields
    const startDateInputs = document.querySelectorAll('input[name="start_date"]');
    const endDateInputs = document.querySelectorAll('input[name="end_date"]');
    
    for (const input of startDateInputs) {
      input.value = formatDate(lastWeek);
    }
    
    for (const input of endDateInputs) {
      input.value = formatDate(today);
    }
  }
  
  function activateTabs() {
    for (const tab of tabs) {
      tab.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Remove active class from all tabs
        for (const t of tabs) {
          t.classList.remove('active');
        }
        
        // Add active class to selected tab
        this.classList.add('active');
        
        // Hide all content containers
        const tabContainers = document.querySelectorAll('.tab-content');
        for (const container of tabContainers) {
          container.style.display = 'none';
        }
        
        // Show selected container
        const targetId = this.getAttribute('href').substring(1);
        document.getElementById(targetId).style.display = 'block';
        
        // Always clear results when switching tabs
        clearResults();
        
        // Special handling for help tab - load help content if needed
        if (targetId === 'help-tab') {
          loadHelpContent();
        }
      });
    }
    
    // Activate first tab by default
    if (tabs.length > 0) {
      tabs[0].click();
    }
    
    // Also activate top navigation
    const navTabs = document.querySelectorAll('nav ul li a');
    for (const navTab of navTabs) {
      navTab.addEventListener('click', function(e) {
        if (this.getAttribute('href').startsWith('#')) {
          e.preventDefault();
          const targetTabId = this.getAttribute('data-tab');
          
          // Remove active class from all nav tabs
          for (const t of navTabs) {
            t.classList.remove('active');
          }
          
          // Add active class to selected nav tab
          this.classList.add('active');
          
          // Find the corresponding tab and click it
          const correspondingTab = Array.from(tabs).find(tab => {
            return tab.getAttribute('href').includes(targetTabId);
          });
          
          if (correspondingTab) {
            correspondingTab.click();
          }
        }
      });
    }
  }
  
  // Function to load help content from help.html
  async function loadHelpContent() {
    const helpContentContainer = document.getElementById('help-content');
    
    // Show loading indicator
    helpContentContainer.innerHTML = `
      <div class="loading">
        <i class="fas fa-spinner"></i>
        <p>Loading help content...</p>
      </div>
    `;
    
    try {
      // Fetch the help.html content
      const response = await fetch('/static/help.html');
      if (!response.ok) {
        throw new Error(`Failed to load help content: ${response.status} ${response.statusText}`);
      }
      
      const html = await response.text();
      
      // Create a temporary element to parse the HTML
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = html;
      
      // Extract styles from the help page
      const styleElements = tempDiv.querySelectorAll('style');
      let stylesContent = '';
      
      for (const styleElement of styleElements) {
        stylesContent += styleElement.outerHTML;
      }
      
      // Also extract any link elements for external stylesheets
      const linkElements = tempDiv.querySelectorAll('link[rel="stylesheet"]');
      let linkContent = '';
      
      for (const linkElement of linkElements) {
        // Only add links that aren't already in the main document
        const href = linkElement.getAttribute('href');
        if (href && !document.querySelector(`link[href="${href}"]`)) {
          linkContent += linkElement.outerHTML;
        }
      }
      
      // Extract the main content
      let helpContent = '';
      const mainElement = tempDiv.querySelector('main');
      
      if (mainElement) {
        helpContent = mainElement.innerHTML;
      } else {
        // Fallback to extract content between <body> and before <footer>
        const bodyContent = tempDiv.querySelector('body');
        if (bodyContent) {
          helpContent = bodyContent.innerHTML;
          
          // Remove header if exists
          const headerContent = tempDiv.querySelector('header');
          if (headerContent) {
            helpContent = helpContent.replace(headerContent.outerHTML, '');
          }
          
          // Remove footer if exists
          const footerContent = tempDiv.querySelector('footer');
          if (footerContent) {
            helpContent = helpContent.replace(footerContent.outerHTML, '');
          }
          
          // Remove scripts
          const scripts = tempDiv.querySelectorAll('script');
          scripts.forEach(script => {
            helpContent = helpContent.replace(script.outerHTML, '');
          });
        }
      }
      
      // Inject styles and content
      helpContentContainer.innerHTML = stylesContent + linkContent + helpContent;
      
      // Initialize any help page specific scripts or behaviors
      initHelpPageBehavior();
      
    } catch (error) {
      console.error('Error loading help content:', error);
      helpContentContainer.innerHTML = `
        <div class="alert alert-error">
          <i class="fas fa-exclamation-circle"></i>
          <p>Error loading help content: ${error.message}</p>
          <button class="btn btn-outlined" onclick="location.href='/static/help.html'">
            Open Help in New Page
          </button>
        </div>
      `;
    }
  }
  
  // Initialize help page behavior (accordion, etc.)
  function initHelpPageBehavior() {
    // Initialize accordions on the help page
    const accordionHeaders = document.querySelectorAll('#help-tab .accordion-header');
    
    for (const header of accordionHeaders) {
      header.addEventListener('click', function() {
        this.classList.toggle('active');
        
        const content = this.nextElementSibling;
        
        if (content.style.maxHeight) {
          content.style.maxHeight = null;
        } else {
          content.style.maxHeight = content.scrollHeight + 'px';
        }
      });
    }
  }
  
  async function handleMarketDataSubmit(e) {
    e.preventDefault();
    
    showLoading(true);
    clearResults();
    
    try {
      const formData = new FormData(marketDataForm);
      const startDate = formData.get('start_date');
      const endDate = formData.get('end_date');
      
      // Call API to get market data
      const response = await fetch(`/api/v1/market-data/?start_date=${startDate}T00:00:00&end_date=${endDate}T23:59:59`);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Check if the response contains test data and message
      const isTestData = data.is_test_data || response.headers.get('X-Test-Data') === 'true';
      const testReason = response.headers.get('X-Test-Reason') || '';
      const message = data.message || '';
      
      // Display results
      displayMarketData(data.data, isTestData, message);
      
      if (isTestData) {
        showAlert(`<i class="fas fa-info-circle"></i> ${message || 'Используются тестовые данные для демонстрации'}`, 'warning');
      } else {
        showAlert('<i class="fas fa-check-circle"></i> Market data successfully loaded', 'success');
      }
      
      // Show clear results button
      if (clearResultsBtn) {
        clearResultsBtn.style.display = 'inline-flex';
      }
    } catch (error) {
      console.error('Error fetching market data:', error);
      showAlert(`<i class="fas fa-exclamation-triangle"></i> Error fetching market data: ${error.message}`, 'danger');
    } finally {
      showLoading(false);
    }
  }
  
  async function handleOptimizationSubmit(e) {
    e.preventDefault();
    
    showLoading(true);
    clearResults();
    
    try {
      const formData = new FormData(optimizationForm);
      const startDate = formData.get('start_date');
      const endDate = formData.get('end_date');
      const threshold = formData.get('threshold') || 0;
      
      // Call API for optimization using POST method (changed back from GET)
      const response = await fetch(`/api/v1/optimization/optimize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          start_date: `${startDate}T00:00:00`,
          end_date: `${endDate}T23:59:59`,
          threshold: Number.parseFloat(threshold)
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || `API Error: ${response.status}`;
        throw new Error(errorMessage);
      }
      
      const data = await response.json();
      
      // Check if data contains a flag indicating test data
      const isTestData = data.is_test_data || response.headers.get('X-Test-Data') === 'true';
      const testReason = response.headers.get('X-Test-Reason') || '';
      const message = data.message || '';
      
      // Display optimization results
      displayOptimizationResults(data.cycles, isTestData, message);
      
      // Save data for CSV download
      if (downloadCsvBtn) {
        downloadCsvBtn.dataset.startDate = startDate;
        downloadCsvBtn.dataset.endDate = endDate;
        downloadCsvBtn.dataset.threshold = threshold;
        downloadCsvBtn.style.display = 'inline-flex';
      }
      
      // Show clear results button
      if (clearResultsBtn) {
        clearResultsBtn.style.display = 'inline-flex';
      }
      
      if (isTestData) {
        showAlert(`<i class="fas fa-info-circle"></i> ${message || 'Используются тестовые данные для демонстрации'}`, 'warning');
      } else {
        showAlert('<i class="fas fa-check-circle"></i> Optimization completed successfully', 'success');
      }
    } catch (error) {
      console.error('Error during optimization:', error);
      showAlert(`<i class="fas fa-exclamation-triangle"></i> Error during optimization: ${error.message}`, 'danger');
    } finally {
      showLoading(false);
    }
  }
  
  async function handleCsvUpload(e) {
    e.preventDefault();
    
    showLoading(true);
    clearResults();
    
    try {
      const formData = new FormData(csvUploadForm);
      
      // Call API to upload CSV
      const response = await fetch('/api/v1/optimization/upload-csv', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || `API Error: ${response.status}`;
        throw new Error(errorMessage);
      }
      
      const data = await response.json();
      
      // Display optimization results
      displayOptimizationResults(data.cycles);
      
      // Show clear results button
      if (clearResultsBtn) {
        clearResultsBtn.style.display = 'inline-flex';
      }
      
      showAlert('<i class="fas fa-check-circle"></i> CSV processed successfully', 'success');
    } catch (error) {
      console.error('Error uploading CSV:', error);
      showAlert(`<i class="fas fa-exclamation-triangle"></i> Error uploading CSV: ${error.message}`, 'danger');
    } finally {
      showLoading(false);
    }
  }
  
  function handleClearResults() {
    clearResults();
    showAlert('<i class="fas fa-broom"></i> Results cleared', 'success');
  }
  
  function displayMarketData(data, isTestData = false, testDataMessage = '') {
    clearResults();
    
    // Get table elements
    const tableBody = document.getElementById('results-table-body');
    const table = document.getElementById('results-table');
    const resultsContainer = document.getElementById('results-container');
    
    // Clear existing data
    tableBody.innerHTML = '';
    
    // Check if data is an array
    if (!Array.isArray(data) || data.length === 0) {
      showAlert('<i class="fas fa-exclamation-triangle"></i> No market data available', 'warning');
      return;
    }
    
    // Set table headers for market data - современный вид
    const thead = table.querySelector('thead tr');
    thead.innerHTML = `
      <th>Date</th>
      <th>Hour</th>
      <th>Price (EUR/kWh)</th>
      <th>Price (ct/kWh)</th>
    `;
    
    // Sort data by date and hour
    const sortedData = [...data].sort((a, b) => {
      // Parse date strings for comparison - handle different formats
      const dateA = a.date.includes('-') ? new Date(a.date) : parseGermanDate(a.date);
      const dateB = b.date.includes('-') ? new Date(b.date) : parseGermanDate(b.date);
      
      if (dateA - dateB !== 0) {
        return dateA - dateB;
      }
      return a.hour - b.hour;
    });
    
    // Create table rows for each data point
    let prevDate = null;
    
    for (const item of sortedData) {
      const row = document.createElement('tr');
      
      // If it's a new date, add some styling
      const dateClass = prevDate === item.date ? 'same-date' : '';
      prevDate = item.date;
      
      const dateDisplay = formatDisplayDate(item.date);
      const hourDisplay = `${item.hour}:00`;
      
      // Calculate price color classes based on value (similar to optimizations)
      const eurPriceClass = getPriceColorClass(item.price_eur, item.hour < 12); // Treat morning hours as "charge"
      
      row.innerHTML = `
        <td>${dateDisplay}</td>
        <td>${hourDisplay}</td>
        <td class="price-cell ${eurPriceClass}">${formatNumber(item.price_eur)}</td>
        <td class="price-cell">${formatNumber(item.price_ct_kwh)}</td>
      `;
      
      tableBody.appendChild(row);
    }
    
    // Add summary information
    displayMarketDataSummary(sortedData, isTestData, testDataMessage);
    
    // Show results with animation
    if (resultsContainer) {
      resultsContainer.style.display = 'block';
      
      // Scroll to results
      setTimeout(() => {
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
    
    // Показываем кнопку очистки
    const clearResultsBtn = document.getElementById('clear-results-btn');
    if (clearResultsBtn) {
      clearResultsBtn.style.display = 'inline-flex';
    }
  }
  
  function parseGermanDate(dateStr) {
    // Parse DD.MM.YYYY format
    const parts = dateStr.split('.');
    if (parts.length === 3) {
      return new Date(parts[2], parts[1] - 1, parts[0]);
    }
    return new Date(dateStr);
  }
  
  function formatDisplayDate(dateStr) {
    // Check if date is in German format (DD.MM.YYYY)
    if (dateStr.includes('.')) {
      return dateStr;
    }
    
    // If in ISO format, convert to DD.MM.YYYY for display
    try {
      const date = new Date(dateStr);
      return `${String(date.getDate()).padStart(2, '0')}.${String(date.getMonth() + 1).padStart(2, '0')}.${date.getFullYear()}`;
    } catch (e) {
      return dateStr;
    }
  }
  
  function displayMarketDataSummary(data, isTestData = false, testDataMessage = '') {
    if (!resultsSummary) return;
    
    // Calculate min, max, avg prices
    const prices = data.map(item => item.price_eur);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const avgPrice = prices.reduce((sum, price) => sum + price, 0) / prices.length;
    
    // Get date range
    const startDate = formatDisplayDate(data[0].date);
    const endDate = formatDisplayDate(data[data.length - 1].date);
    
    // Create HTML for summary
    let summaryHTML = `
      <h3>Market Data Summary ${isTestData ? '(Simulated Data)' : ''}</h3>
    `;
    
    // Add test data warning if applicable
    if (isTestData) {
      summaryHTML += `
        <div class="alert alert-warning">
          <i class="fas fa-info-circle"></i> ${testDataMessage || 'Using simulated data for demonstration'}
        </div>
      `;
    }
    
    summaryHTML += `
      <div class="summary-stats">
        <div class="stat-row">
          <span class="stat-label">Date Range:</span>
          <span class="stat-value">${startDate} - ${endDate}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Total Records:</span>
          <span class="stat-value">${data.length}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Min Price:</span>
          <span class="stat-value">${formatNumber(minPrice)} EUR/kWh</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Max Price:</span>
          <span class="stat-value">${formatNumber(maxPrice)} EUR/kWh</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Avg Price:</span>
          <span class="stat-value">${formatNumber(avgPrice)} EUR/kWh</span>
        </div>
      </div>
    `;
    
    resultsSummary.innerHTML = summaryHTML;
  }
  
  function formatNumber(num) {
    // Проверяем, является ли num числом и не является ли NaN
    if (num === undefined || num === null || isNaN(num)) {
      return '—'; // Используем длинное тире вместо NaN
    }
    return (Math.round(num * 10000) / 10000).toLocaleString('de-DE', {
      minimumFractionDigits: 4,
      maximumFractionDigits: 4
    });
  }
  
  function formatCurrency(num) {
    // Проверяем, является ли num числом и не является ли NaN
    if (num === undefined || num === null || isNaN(num)) {
      return '—'; // Используем длинное тире вместо NaN
    }
    return (Math.round(num * 100) / 100).toLocaleString('de-DE', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }
  
  // Get profit color based on value
  function getProfitColorClass(profit) {
    // Apply color classes based on profit amount
    if (profit >= 10) {
      return 'high-profit'; // High profit - green
    } else if (profit >= 5) {
      return 'medium-profit'; // Medium profit - orange
    } else {
      return 'low-profit'; // Low profit - red
    }
  }
  
  // Get price color based on charge or discharge
  function getPriceColorClass(price, isCharge) {
    // For charge price, lower is better
    // For discharge price, higher is better
    if (isCharge) {
      if (price < 10) {
        return 'high-profit'; // Low charge price is good - green
      } else if (price < 15) {
        return 'medium-profit'; // Medium charge price - orange
      } else {
        return 'low-profit'; // High charge price is bad - red
      }
    } else {
      if (price > 20) {
        return 'high-profit'; // High discharge price is good - green
      } else if (price > 15) {
        return 'medium-profit'; // Medium discharge price - orange
      } else {
        return 'low-profit'; // Low discharge price is bad - red
      }
    }
  }
  
  function displayOptimizationResults(cycles, isTestData = false, testDataMessage = '') {
    // Get table elements
    const tableBody = document.getElementById('results-table-body');
    const table = document.getElementById('results-table');
    const resultsContainer = document.getElementById('results-container');
    
    // Clear existing data
    tableBody.innerHTML = '';
    
    if (!cycles || cycles.length === 0) {
      const messageRow = `
        <tr>
          <td colspan="8" style="text-align: center;">No profit cycles found with the specified threshold.</td>
        </tr>
      `;
      tableBody.innerHTML = messageRow;
      resultsContainer.style.display = 'block';
      
      // Set table headers
      const thead = table.querySelector('thead tr');
      thead.innerHTML = '<th>Message</th>';
      
      // Scroll to results
      resultsContainer.scrollIntoView({ behavior: 'smooth' });
      return;
    }
    
    // Set table headers
    const thead = table.querySelector('thead tr');
    thead.innerHTML = `
      <th>Date</th>
      <th>Charge Time</th>
      <th>Charge Price (ct/kWh)</th>
      <th>Discharge Time</th>
      <th>Discharge Price (ct/kWh)</th>
      <th>Difference (ct/kWh)</th>
      <th>Profit (EUR)</th>
      <th>Profit After Losses (EUR)</th>
    `;
    
    // Add data rows
    cycles.forEach(cycle => {
      const row = document.createElement('tr');
      
      // Format date
      const date = formatDisplayDate(cycle.date);
      
      // Проверяем наличие значений и устанавливаем значения по умолчанию
      const chargeHour = cycle.charge_hour !== undefined ? cycle.charge_hour : '--';
      const dischargeHour = cycle.discharge_hour !== undefined ? cycle.discharge_hour : '--';
      const chargePrice = cycle.charge_price !== undefined ? cycle.charge_price : 0;
      const dischargePrice = cycle.discharge_price !== undefined ? cycle.discharge_price : 0;
      const priceDifference = cycle.price_difference !== undefined ? cycle.price_difference : 
                             (chargePrice !== 0 && dischargePrice !== 0 ? (dischargePrice - chargePrice) : 0);
      const profit = cycle.profit !== undefined ? cycle.profit : 0;
      const profitAfterLosses = cycle.profit_after_losses !== undefined ? cycle.profit_after_losses : 0;
      
      // Calculate profit classes
      const chargePriceClass = getPriceColorClass(chargePrice, true);
      const dischargePriceClass = getPriceColorClass(dischargePrice, false);
      const profitClass = getProfitColorClass(profitAfterLosses);
      
      // Форматируем отображение времени
      const chargeTimeDisplay = chargeHour !== '--' ? `${chargeHour}:00` : '--';
      const dischargeTimeDisplay = dischargeHour !== '--' ? `${dischargeHour}:00` : '--';
      
      row.innerHTML = `
        <td>${date}</td>
        <td>${chargeTimeDisplay}</td>
        <td class="price-cell ${chargePriceClass}">${formatNumber(chargePrice)}</td>
        <td>${dischargeTimeDisplay}</td>
        <td class="price-cell ${dischargePriceClass}">${formatNumber(dischargePrice)}</td>
        <td>${formatNumber(priceDifference)}</td>
        <td class="profit-cell">${formatCurrency(profit)}</td>
        <td class="profit-cell ${profitClass}">${formatCurrency(profitAfterLosses)}</td>
      `;
      
      tableBody.appendChild(row);
    });
    
    // Display summary
    displayOptimizationSummary(cycles, isTestData, testDataMessage);
    
    // Show results container with animation
    resultsContainer.style.display = 'block';
    
    // Scroll to results
    setTimeout(() => {
      resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  }
  
  function displayOptimizationSummary(cycles, isTestData = false, testDataMessage = '') {
    if (!resultsSummary) return;
    
    // Calculate total profit
    const totalProfit = cycles.reduce((sum, cycle) => sum + Number.parseFloat(cycle.profit), 0);
    
    // Calculate average profit per cycle
    const avgProfit = totalProfit / cycles.length;
    
    // Find max profit cycle
    const maxProfitCycle = cycles.reduce((max, cycle) => 
      Number.parseFloat(cycle.profit) > Number.parseFloat(max.profit) ? cycle : max, cycles[0]);
    
    // Find most profitable date
    const dateWithMaxProfit = maxProfitCycle.date;
    
    // Create HTML for summary
    let summaryHTML = `
      <h3>Optimization Summary ${isTestData ? '(Simulated Data)' : ''}</h3>
    `;
    
    // Add test data warning if applicable
    if (isTestData) {
      summaryHTML += `
        <div class="test-data-notice">
          <i class="fas fa-info-circle"></i> API Error: ${testDataMessage || 'Using test data.'}
        </div>
      `;
    }
    
    summaryHTML += `
      <div class="summary-stats">
        <div class="stat-row">
          <span class="stat-label">Cycles found:</span>
          <span class="stat-value">${cycles.length}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Total profit:</span>
          <span class="stat-value">${formatCurrency(totalProfit)} €</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Average profit per cycle:</span>
          <span class="stat-value">${formatCurrency(avgProfit)} €</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Maximum profit:</span>
          <span class="stat-value">${formatCurrency(maxProfitCycle.profit)} € (${dateWithMaxProfit})</span>
        </div>
      </div>
      
      <div class="color-legend">
        <h4>Color Legend</h4>
        <div class="legend-item">
          <span class="legend-color high-profit">■</span>
          <span class="legend-label">High profit (≥ 10 €)</span>
        </div>
        <div class="legend-item">
          <span class="legend-color medium-profit">■</span>
          <span class="legend-label">Medium profit (5-10 €)</span>
        </div>
        <div class="legend-item">
          <span class="legend-color low-profit">■</span>
          <span class="legend-label">Low profit (< 5 €)</span>
        </div>
        <div class="legend-item">
          <span class="legend-color good-price">■</span>
          <span class="legend-label">Good price (charging: < 0.05 € / discharging: > 0.15 €)</span>
        </div>
        <div class="legend-item">
          <span class="legend-color medium-price">■</span>
          <span class="legend-label">Medium price (charging: 0.05-0.1 € / discharging: 0.1-0.15 €)</span>
        </div>
        <div class="legend-item">
          <span class="legend-color high-price">■</span>
          <span class="legend-label">Poor price (charging: > 0.1 € / discharging: < 0.1 €)</span>
        </div>
      </div>
    `;
    
    resultsSummary.innerHTML = summaryHTML;
    resultsSummary.style.display = 'block';
  }
  
  function showLoading(show) {
    if (loadingIndicator) {
      loadingIndicator.style.display = show ? 'block' : 'none';
    }
  }
  
  function clearResults() {
    if (resultsTableBody) {
      resultsTableBody.innerHTML = '';
    }
    
    if (resultsSummary) {
      resultsSummary.innerHTML = '';
      resultsSummary.style.display = 'none';
    }
    
    if (alertContainer) {
      alertContainer.innerHTML = '';
    }
    
    if (downloadCsvBtn) {
      downloadCsvBtn.style.display = 'none';
    }
    
    if (clearResultsBtn) {
      clearResultsBtn.style.display = 'none';
    }
    
    // Скрываем контейнер результатов
    const resultsContainer = document.getElementById('results-container');
    if (resultsContainer) {
      resultsContainer.classList.remove('visible');
      resultsContainer.style.display = 'none';
    }
  }
  
  function showAlert(message, type) {
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = message;
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'close';
    closeBtn.innerHTML = '&times;';
    closeBtn.addEventListener('click', function() {
      alert.remove();
    });
    
    alert.appendChild(closeBtn);
    alertContainer.appendChild(alert);
    
    // Automatically hide notification after 5 seconds
    setTimeout(() => {
      alert.style.opacity = '0';
      setTimeout(() => {
        alert.remove();
      }, 300);
    }, 5000);
  }
  
  // Handler for CSV download button
  if (downloadCsvBtn) {
    downloadCsvBtn.addEventListener('click', async function() {
      const startDate = this.dataset.startDate;
      const endDate = this.dataset.endDate;
      const threshold = this.dataset.threshold || 0;
      const useTestData = this.dataset.useTestData === 'true';
      
      try {
        // Используем запрос к API с параметрами в строке запроса
        const response = await fetch(`/api/v1/optimization/optimize-csv?start_date=${startDate}T00:00:00&end_date=${endDate}T23:59:59&threshold=${threshold}${useTestData ? '&use_test_data=true' : ''}`, {
          method: 'POST'
        });
        
        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`);
        }
        
        const csvContent = await response.text();
        
        // Create download link
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `optimization_results_${startDate}_${endDate}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showAlert('<i class="fas fa-check-circle"></i> CSV file downloaded successfully', 'success');
      } catch (error) {
        console.error('Error downloading CSV:', error);
        showAlert(`<i class="fas fa-exclamation-triangle"></i> Error downloading CSV: ${error.message}`, 'danger');
      }
    });
  }
});