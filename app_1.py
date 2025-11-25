<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mason Data Explorer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- XLSX Library for parsing Excel files -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <!-- Chosen Palette: Warm Neutrals (Slate/Indigo) -->
    <!-- Application Structure Plan: The static table report is transformed into a dynamic, single-page dashboard. The Information Architecture consists of four key areas: 1) Header with title and Upload, 2) Key Performance Indicators (KPIs/Metrics), 3) Filter & Controls section (including new "No Products" filter), 4) Data Display area (with Call buttons), and 5) Visualizations. -->
    <!-- Visualization & Content Choices:
        - [Report Info] Excel Import -> [Goal] Load external data -> [Viz/Method] File Input + SheetJS. [Interaction] Parse file -> Merge/Replace Data -> Re-render.
        - [Report Info] Contact Number -> [Goal] Action -> [Viz/Method] <a href="tel:"> button. [Interaction] Click to call.
        - [Report Info] Zero Products -> [Goal] Filter -> [Viz/Method] Checkbox. [Interaction] Filter logic checks for empty product array.
    -->
    <!-- CONFIRMATION: NO SVG graphics used. NO Mermaid JS used. -->
    <style>
      .chart-container {
        position: relative;
        width: 100%;
        max-width: 600px;
        height: 350px;
        margin-left: auto;
        margin-right: auto;
      }
      @media (max-width: 768px) {
        .chart-container {
          height: 300px;
        }
      }
      body {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
      }
    </style>
</head>
<body class="bg-slate-50 font-sans text-slate-800">

    <header class="bg-white shadow-md w-full sticky top-0 z-50">
        <div class="container mx-auto px-4 py-4 md:px-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <h1 class="text-3xl font-bold text-indigo-700">Mason Data Explorer</h1>
            
            <div class="flex items-center gap-2">
                <input type="file" id="excel-upload" accept=".xlsx, .xls" class="hidden" />
                <label for="excel-upload" class="cursor-pointer inline-flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-md shadow-sm transition-colors">
                    📂 Import Excel File
                </label>
                <span id="file-name" class="text-xs text-slate-500 italic hidden md:block"></span>
            </div>
        </div>
    </header>

    <main class="container mx-auto p-4 md:p-8">

        <section class="mb-8">
            <p class="text-lg text-slate-700 mb-6">
                Welcome to the interactive Mason Data Explorer. Upload your Excel sheet to visualize your data, or explore the sample data below. Use filters to narrow down the list and click "Call" to contact masons directly.
            </p>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="bg-white p-5 rounded-lg shadow text-center">
                    <h3 class="text-sm font-semibold text-slate-500 uppercase">Total Masons</h3>
                    <p id="metric-total" class="text-4xl font-bold text-indigo-600">10</p>
                </div>
                <div class="bg-white p-5 rounded-lg shadow text-center">
                    <h3 class="text-sm font-semibold text-slate-500 uppercase">Displaying</h3>
                    <p id="metric-displaying" class="text-4xl font-bold text-indigo-600">10</p>
                </div>
                <div class="bg-white p-5 rounded-lg shadow text-center">
                    <h3 class="text-sm font-semibold text-slate-500 uppercase">Locations</h3>
                    <p id="metric-locations" class="text-4xl font-bold text-indigo-600">0</p>
                </div>
                <div class="bg-white p-5 rounded-lg shadow text-center">
                    <h3 class="text-sm font-semibold text-slate-500 uppercase">DLRs</h3>
                    <p id="metric-dlrs" class="text-4xl font-bold text-indigo-600">0</p>
                </div>
            </div>
        </section>

        <section class="bg-white p-5 md:p-6 rounded-lg shadow mb-8">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-xl font-bold text-slate-700">Filters</h2>
                <button id="reset-filters" class="text-sm text-indigo-600 hover:text-indigo-800 font-medium">🔄 Reset Filters</button>
            </div>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                    <label for="filter-location" class="block text-sm font-medium text-slate-600 mb-1">Location</label>
                    <select id="filter-location" class="w-full rounded-md border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
                        <option value="all">All Locations</option>
                    </select>
                </div>
                <div>
                    <label for="filter-dlr" class="block text-sm font-medium text-slate-600 mb-1">DLR Name</label>
                    <select id="filter-dlr" class="w-full rounded-md border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
                        <option value="all">All DLRs</option>
                    </select>
                </div>
                <div>
                    <label for="filter-day" class="block text-sm font-medium text-slate-600 mb-1">Day</label>
                    <select id="filter-day" class="w-full rounded-md border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
                        <option value="all">All Days</option>
                        <option value="MONDAY">Monday</option>
                        <option value="TUESDAY">Tuesday</option>
                        <option value="WEDNESDAY">Wednesday</option>
                        <option value="THURSDAY">Thursday</option>
                        <option value="FRIDAY">Friday</option>
                        <option value="SATURDAY">Saturday</option>
                        <option value="SUNDAY">Sunday</option>
                    </select>
                </div>
                <div>
                    <label for="filter-category" class="block text-sm font-medium text-slate-600 mb-1">Category</label>
                    <select id="filter-category" class="w-full rounded-md border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
                        <option value="all">All Categories</option>
                        <option value="E">Category E</option>
                        <option value="M">Category M</option>
                    </select>
                </div>
            </div>
            <div class="mt-4 pt-4 border-t border-slate-200">
                <div class="flex flex-col md:flex-row gap-6">
                    <div class="flex-grow">
                        <label class="block text-sm font-medium text-slate-600 mb-2">Products (must have all selected)</label>
                        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-x-4 gap-y-2">
                            <div class="flex items-center">
                                <input id="filter-hw305" data-product="HW305" type="checkbox" class="filter-product h-4 w-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500">
                                <label for="filter-hw305" class="ml-2 text-sm text-slate-700">HW305</label>
                            </div>
                            <div class="flex items-center">
                                <input id="filter-hw101" data-product="HW101" type="checkbox" class="filter-product h-4 w-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500">
                                <label for="filter-hw101" class="ml-2 text-sm text-slate-700">HW101</label>
                            </div>
                            <div class="flex items-center">
                                <input id="filter-hw201" data-product="Hw201" type="checkbox" class="filter-product h-4 w-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500">
                                <label for="filter-hw201" class="ml-2 text-sm text-slate-700">Hw201</label>
                            </div>
                            <div class="flex items-center">
                                <input id="filter-hw103" data-product="HW103" type="checkbox" class="filter-product h-4 w-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500">
                                <label for="filter-hw103" class="ml-2 text-sm text-slate-700">HW103</label>
                            </div>
                            <div class="flex items-center">
                                <input id="filter-hw302" data-product="HW302" type="checkbox" class="filter-product h-4 w-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500">
                                <label for="filter-hw302" class="ml-2 text-sm text-slate-700">HW302</label>
                            </div>
                            <div class="flex items-center">
                                <input id="filter-hw310" data-product="HW310" type="checkbox" class="filter-product h-4 w-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500">
                                <label for="filter-hw310" class="ml-2 text-sm text-slate-700">HW310</label>
                            </div>
                        </div>
                    </div>
                    <div class="md:border-l border-slate-200 md:pl-6 min-w-[200px]">
                         <label class="block text-sm font-medium text-slate-600 mb-2">Special Filters</label>
                         <div class="flex items-center bg-amber-50 p-2 rounded border border-amber-200">
                            <input id="filter-no-products" type="checkbox" class="h-4 w-4 text-amber-600 border-slate-300 rounded focus:ring-amber-500">
                            <label for="filter-no-products" class="ml-2 text-sm font-medium text-slate-800">Show Masons with No Products</label>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="mb-8">
            <h2 class="text-2xl font-bold text-slate-800 mb-6 text-center">Data Visualizations</h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div class="bg-white p-5 rounded-lg shadow">
                    <h3 class="text-lg font-semibold text-slate-700 text-center mb-4">Masons per Location</h3>
                    <div class="chart-container">
                        <canvas id="locationChart"></canvas>
                    </div>
                </div>
                <div class="bg-white p-5 rounded-lg shadow">
                    <h3 class="text-lg font-semibold text-slate-700 text-center mb-4">Masons per Day</h3>
                    <div class="chart-container">
                        <canvas id="dayChart"></canvas>
                    </div>
                </div>
                <div class="bg-white p-5 rounded-lg shadow">
                    <h3 class="text-lg font-semibold text-slate-700 text-center mb-4">Product Popularity</h3>
                    <div class="chart-container">
                        <canvas id="productChart"></canvas>
                    </div>
                </div>
                <div class="bg-white p-5 rounded-lg shadow">
                    <h3 class="text-lg font-semibold text-slate-700 text-center mb-4">Category Distribution</h3>
                    <div class="chart-container">
                        <canvas id="categoryChart"></canvas>
                    </div>
                </div>
            </div>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-slate-800 mb-6">Mason Directory</h2>
            <div id="mason-list-container" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            </div>
            <div id="no-results" class="hidden text-center bg-white p-10 rounded-lg shadow">
                <p class="text-2xl font-semibold text-slate-700">No Masons Found</p>
                <p class="text-slate-500 mt-2">Try adjusting your filter criteria.</p>
            </div>
        </section>

    </main>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            // Using 'let' to allow data updates from Excel upload
            let masonData = [
                { id: 1, code: 'M100258', name: 'C.PRABHAKARAN', contact: '9487049215', dlr: 'RAJA TRADERS', location: 'TIRUCHENDUR', day: 'MONDAY', category: 'E', products: ['HW305', 'HW101', 'Hw201', 'HW103'] },
                { id: 2, code: 'M100259', name: 'C.SUDHAKARAN', contact: '9443460152', dlr: 'RAJA TRADERS', location: 'TIRUCHENDUR', day: 'MONDAY', category: 'E', products: ['HW305', 'HW101', 'Hw201', 'HW103'] },
                { id: 3, code: 'M100260', name: 'PECHIMUTHU', contact: '9842120938', dlr: 'SRI VALLI AGENCY', location: 'ALWARTHIRINAGRI', day: 'SATURDAY', category: 'E', products: ['HW305', 'HW101', 'Hw201'] },
                { id: 4, code: 'M100261', name: 'E.ENAMUTHU', contact: '9952073043', dlr: 'SRI VALLI AGENCY', location: 'ALWARTHIRINAGRI', day: 'SATURDAY', category: 'E', products: [] },
                { id: 5, code: 'M100262', name: 'K.MURUGAN', contact: '9842367551', dlr: 'SRI VALLI AGENCY', location: 'ALWARTHIRINAGRI', day: 'SATURDAY', category: 'E', products: [] },
                { id: 6, code: 'M100263', name: 'PERUMAL', contact: '9486204932', dlr: 'SUNDER RAJ HARDWARES', location: 'PEKULAM', day: 'FRIDAY', category: 'E', products: ['HW305', 'HW101', 'Hw201'] },
                { id: 7, code: 'M100264', name: 'M.KALIMUTHU', contact: '8526525676', dlr: 'SUNDER RAJ HARDWARES', location: 'PEKULAM', day: 'FRIDAY', category: 'M', products: [] },
                { id: 8, code: 'M100265', name: 'T.ANTONY', contact: '9944329680', dlr: '', location: 'KAYALPATNAM', day: 'TUESDAY', category: 'M', products: [] },
                { id: 9, code: 'M100266', name: 'THANGARAJ', contact: '9976110550', dlr: 'PERUMAL KONAR SONS', location: 'SRIVAIGUNDAM', day: 'THURSDAY', category: 'E', products: ['HW305', 'HW101'] },
                { id: 10, code: 'M100267', name: 'A.SUBRAMANIAN', contact: '9659517567', dlr: 'SRI SAKTHI ELECTRICALS', location: 'SEIDHUNGANALLUR', day: 'THURSDAY', category: 'E', products: ['Hw201'] }
            ];

            const currentFilters = {
                location: 'all',
                dlr: 'all',
                day: 'all',
                category: 'all',
                products: [],
                noProducts: false
            };

            // DOM Elements
            const filterLocationEl = document.getElementById('filter-location');
            const filterDlrEl = document.getElementById('filter-dlr');
            const filterDayEl = document.getElementById('filter-day');
            const filterCategoryEl = document.getElementById('filter-category');
            const filterProductEls = document.querySelectorAll('.filter-product');
            const filterNoProductsEl = document.getElementById('filter-no-products');
            const resetFiltersEl = document.getElementById('reset-filters');
            const masonListContainer = document.getElementById('mason-list-container');
            const noResultsEl = document.getElementById('no-results');
            
            // Metrics Elements
            const metricDisplayingEl = document.getElementById('metric-displaying');
            const metricTotalEl = document.getElementById('metric-total');
            const metricLocationsEl = document.getElementById('metric-locations');
            const metricDlrsEl = document.getElementById('metric-dlrs');

            // Excel Elements
            const excelUploadInput = document.getElementById('excel-upload');
            const fileNameDisplay = document.getElementById('file-name');

            // Chart Instances (to destroy/recreate)
            let charts = {};

            function populateFilterOptions() {
                // Clear existing options except 'All'
                filterLocationEl.innerHTML = '<option value="all">All Locations</option>';
                filterDlrEl.innerHTML = '<option value="all">All DLRs</option>';

                const locations = [...new Set(masonData.map(m => m.location))].sort();
                const dlrs = [...new Set(masonData.map(m => m.dlr).filter(d => d))].sort();

                locations.forEach(location => {
                    const option = document.createElement('option');
                    option.value = location;
                    option.textContent = location;
                    filterLocationEl.appendChild(option);
                });

                dlrs.forEach(dlr => {
                    const option = document.createElement('option');
                    option.value = dlr;
                    option.textContent = dlr;
                    filterDlrEl.appendChild(option);
                });
                
                metricTotalEl.textContent = masonData.length;
                metricLocationsEl.textContent = locations.length;
                metricDlrsEl.textContent = dlrs.length;
            }

            function renderMasonList(data) {
                masonListContainer.innerHTML = '';
                
                if (data.length === 0) {
                    noResultsEl.classList.remove('hidden');
                } else {
                    noResultsEl.classList.add('hidden');
                }

                metricDisplayingEl.textContent = data.length;

                data.forEach(mason => {
                    const productList = mason.products.length > 0 
                        ? mason.products.map(p => `<span class="inline-block bg-indigo-100 text-indigo-800 text-xs font-medium px-2.5 py-0.5 rounded-full border border-indigo-200">${p}</span>`).join(' ')
                        : '<span class="text-xs text-slate-400 italic">No products listed</span>';
                    
                    const callButton = mason.contact 
                        ? `<a href="tel:${mason.contact}" class="inline-flex items-center justify-center w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md transition-colors mt-3">
                             <span class="mr-2">📞</span> Call Now
                           </a>`
                        : `<button disabled class="inline-flex items-center justify-center w-full px-4 py-2 bg-slate-300 text-slate-500 text-sm font-medium rounded-md mt-3 cursor-not-allowed">
                             No Contact
                           </button>`;

                    const card = `
                        <div class="bg-white rounded-lg shadow p-5 flex flex-col transition-all duration-300 hover:shadow-lg border-t-4 border-indigo-500">
                            <div class="mb-3">
                                <h3 class="text-xl font-bold text-slate-800">${mason.name}</h3>
                                <div class="flex justify-between items-center">
                                    <p class="text-sm text-slate-500 font-medium">${mason.code || 'No Code'}</p>
                                    <span class="bg-slate-100 text-slate-600 text-xs px-2 py-1 rounded">${mason.category || 'N/A'}</span>
                                </div>
                            </div>
                            <div class="space-y-2 text-sm text-slate-700 mb-4 flex-grow">
                                <p class="flex items-start"><span class="w-24 font-semibold text-slate-500">Contact:</span> ${mason.contact || 'N/A'}</p>
                                <p class="flex items-start"><span class="w-24 font-semibold text-slate-500">Location:</span> ${mason.location || 'N/A'}</p>
                                <p class="flex items-start"><span class="w-24 font-semibold text-slate-500">DLR:</span> ${mason.dlr || 'N/A'}</p>
                                <p class="flex items-start"><span class="w-24 font-semibold text-slate-500">Day:</span> <span class="font-semibold text-indigo-700">${mason.day || 'N/A'}</span></p>
                            </div>
                            <div class="mt-auto pt-3 border-t border-slate-200">
                                <h4 class="text-xs font-semibold text-slate-600 mb-2">Products:</h4>
                                <div class="flex flex-wrap gap-2 mb-3">
                                    ${productList}
                                </div>
                                ${callButton}
                            </div>
                        </div>
                    `;
                    masonListContainer.innerHTML += card;
                });
            }

            function applyFilters() {
                let filteredData = [...masonData];

                // Standard Filters
                if (currentFilters.location !== 'all') {
                    filteredData = filteredData.filter(m => m.location === currentFilters.location);
                }
                if (currentFilters.dlr !== 'all') {
                    filteredData = filteredData.filter(m => m.dlr === currentFilters.dlr);
                }
                if (currentFilters.day !== 'all') {
                    filteredData = filteredData.filter(m => m.day === currentFilters.day);
                }
                if (currentFilters.category !== 'all') {
                    filteredData = filteredData.filter(m => m.category === currentFilters.category);
                }

                // Product Logic
                if (currentFilters.noProducts) {
                    // If "No Products" is checked, ONLY show masons with 0 products
                    filteredData = filteredData.filter(m => m.products.length === 0);
                    
                    // Disable product checkboxes visually or logically if needed, 
                    // but simple filter priority (No Products > Specific Products) works fine for UX.
                } else if (currentFilters.products.length > 0) {
                    // Standard product filtering
                    filteredData = filteredData.filter(m => 
                        currentFilters.products.every(p => m.products.includes(p))
                    );
                }
                
                renderMasonList(filteredData);
            }

            function updateFilters() {
                currentFilters.location = filterLocationEl.value;
                currentFilters.dlr = filterDlrEl.value;
                currentFilters.day = filterDayEl.value;
                currentFilters.category = filterCategoryEl.value;
                currentFilters.noProducts = filterNoProductsEl.checked;
                
                currentFilters.products = [];
                filterProductEls.forEach(checkbox => {
                    if (checkbox.checked) {
                        currentFilters.products.push(checkbox.dataset.product);
                    }
                });
                
                applyFilters();
            }

            function resetFilters() {
                filterLocationEl.value = 'all';
                filterDlrEl.value = 'all';
                filterDayEl.value = 'all';
                filterCategoryEl.value = 'all';
                filterNoProductsEl.checked = false;
                filterProductEls.forEach(checkbox => checkbox.checked = false);
                
                updateFilters();
            }

            // Excel Upload Logic
            excelUploadInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (!file) return;

                fileNameDisplay.textContent = `File: ${file.name}`;

                const reader = new FileReader();
                reader.onload = function(e) {
                    const data = new Uint8Array(e.target.result);
                    const workbook = XLSX.read(data, { type: 'array' });
                    
                    // Assume first sheet is the target
                    const firstSheetName = workbook.SheetNames[0];
                    const worksheet = workbook.Sheets[firstSheetName];
                    const jsonData = XLSX.utils.sheet_to_json(worksheet);

                    // Transform Excel Data to App Data Structure
                    const transformedData = jsonData.map((row, index) => {
                        // Detect Products based on 'YES' or similar values in specific columns
                        const products = [];
                        const productCols = ['HW305', 'HW101', 'Hw201', 'HW201', 'HW103', 'HW302', 'HW310']; // Handle case variations
                        
                        productCols.forEach(p => {
                            if (row[p] && String(row[p]).toUpperCase().includes('YES')) {
                                products.push(p.toUpperCase()); // Standardize to uppercase
                            }
                        });

                        return {
                            id: index + 1,
                            code: row['MASON CODE'] || row['Mason Code'] || '',
                            name: row['MASON NAME'] || row['Mason Name'] || 'Unknown',
                            contact: row['CONTACT NUMBER'] || row['Contact Number'] || '',
                            dlr: row['DLR NAME'] || row['DLR Name'] || '',
                            location: row['Location'] || row['LOCATION'] || '',
                            day: row['DAY'] || row['Day'] || '',
                            category: row['Category'] || row['CATEGORY'] || '',
                            products: products
                        };
                    });

                    // Update Global Data
                    if (transformedData.length > 0) {
                        masonData = transformedData;
                        
                        // Re-initialize app
                        populateFilterOptions();
                        renderMasonList(masonData);
                        createCharts(); // Re-draw charts with new data
                        resetFilters();
                        alert(`Successfully loaded ${transformedData.length} masons from Excel!`);
                    } else {
                        alert('No valid data found in the Excel file.');
                    }
                };
                reader.readAsArrayBuffer(file);
            });


            function createCharts() {
                // Destroy existing charts if they exist
                if (charts.location) charts.location.destroy();
                if (charts.day) charts.day.destroy();
                if (charts.product) charts.product.destroy();
                if (charts.category) charts.category.destroy();

                const chartColors = {
                    bg: [
                        'rgba(79, 70, 229, 0.2)',  // indigo
                        'rgba(59, 130, 246, 0.2)', // blue
                        'rgba(14, 165, 233, 0.2)', // sky
                        'rgba(16, 185, 129, 0.2)', // emerald
                        'rgba(245, 158, 11, 0.2)', // amber
                        'rgba(239, 68, 68, 0.2)',  // red
                        'rgba(139, 92, 246, 0.2)'  // violet
                    ],
                    border: [
                        'rgba(79, 70, 229, 1)',
                        'rgba(59, 130, 246, 1)',
                        'rgba(14, 165, 233, 1)',
                        'rgba(16, 185, 129, 1)',
                        'rgba(245, 158, 11, 1)',
                        'rgba(239, 68, 68, 1)',
                        'rgba(139, 92, 246, 1)'
                    ]
                };

                const chartOptions = {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { precision: 0 }
                        }
                    }
                };
                
                const horizontalChartOptions = {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: { precision: 0 }
                        }
                    }
                };

                const doughnutChartOptions = {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                        }
                    }
                };

                const locationData = masonData.reduce((acc, m) => {
                    const loc = m.location || 'Unknown';
                    acc[loc] = (acc[loc] || 0) + 1;
                    return acc;
                }, {});
                charts.location = new Chart(document.getElementById('locationChart').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: Object.keys(locationData),
                        datasets: [{
                            label: 'Masons',
                            data: Object.values(locationData),
                            backgroundColor: chartColors.bg,
                            borderColor: chartColors.border,
                            borderWidth: 1
                        }]
                    },
                    options: chartOptions
                });

                const dayData = masonData.reduce((acc, m) => {
                    const d = m.day || 'Unknown';
                    acc[d] = (acc[d] || 0) + 1;
                    return acc;
                }, {});
                
                // Sort days roughly in order if possible
                const dayOrder = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'];
                const sortedDays = Object.keys(dayData).sort((a, b) => {
                     return dayOrder.indexOf(a.toUpperCase()) - dayOrder.indexOf(b.toUpperCase());
                });

                charts.day = new Chart(document.getElementById('dayChart').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: sortedDays.map(d => d.charAt(0) + d.slice(1).toLowerCase()),
                        datasets: [{
                            label: 'Masons',
                            data: sortedDays.map(d => dayData[d]),
                            backgroundColor: chartColors.bg,
                            borderColor: chartColors.border,
                            borderWidth: 1
                        }]
                    },
                    options: chartOptions
                });

                const productData = masonData.reduce((acc, m) => {
                    m.products.forEach(p => {
                        acc[p] = (acc[p] || 0) + 1;
                    });
                    return acc;
                }, {});
                charts.product = new Chart(document.getElementById('productChart').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: Object.keys(productData),
                        datasets: [{
                            label: 'Masons',
                            data: Object.values(productData),
                            backgroundColor: chartColors.bg,
                            borderColor: chartColors.border,
                            borderWidth: 1
                        }]
                    },
                    options: horizontalChartOptions
                });

                const categoryData = masonData.reduce((acc, m) => {
                    const cat = m.category || 'Unknown';
                    acc[cat] = (acc[cat] || 0) + 1;
                    return acc;
                }, {});
                charts.category = new Chart(document.getElementById('categoryChart').getContext('2d'), {
                    type: 'doughnut',
                    data: {
                        labels: Object.keys(categoryData).map(c => `Category ${c}`),
                        datasets: [{
                            data: Object.values(categoryData),
                            backgroundColor: [chartColors.bg[0], chartColors.bg[1], chartColors.bg[2]],
                            borderColor: [chartColors.border[0], chartColors.border[1], chartColors.border[2]],
                            borderWidth: 1
                        }]
                    },
                    options: doughnutChartOptions
                });
            }

            filterLocationEl.addEventListener('change', updateFilters);
            filterDlrEl.addEventListener('change', updateFilters);
            filterDayEl.addEventListener('change', updateFilters);
            filterCategoryEl.addEventListener('change', updateFilters);
            filterNoProductsEl.addEventListener('change', updateFilters);
            filterProductEls.forEach(el => el.addEventListener('change', updateFilters));
            resetFiltersEl.addEventListener('click', resetFilters);

            populateFilterOptions();
            renderMasonList(masonData);
            createCharts();
        });
    </script>
</body>
</html>
