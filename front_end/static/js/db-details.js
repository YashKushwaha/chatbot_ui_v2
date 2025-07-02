// ====================== FETCH FUNCTIONS ======================

async function fetchDatabases() {
    const response = await fetch('/mongo/list-databases');
    if (!response.ok) throw new Error('Failed to fetch databases');
    const data = await response.json();
    return data.databases || [];
}

async function fetchCollections(dbName) {
    const response = await fetch(`/mongo/list-collections?db=${encodeURIComponent(dbName)}`);
    if (!response.ok) throw new Error('Failed to fetch collections');
    const data = await response.json();
    return data.collections || [];
}

async function fetchNumRecords(db, collection) {
    const response = await fetch(`/mongo/num-records-in-collection?db=${encodeURIComponent(db)}&collection=${encodeURIComponent(collection)}`);
    if (!response.ok) throw new Error('Failed to fetch number of records');
    const data = await response.json();
    return data.num_records || 0;
}

async function fetchFirstNRecords(db, collection) {
    const response = await fetch(`/mongo/first-n-records-in-collection?db=${encodeURIComponent(db)}&collection=${encodeURIComponent(collection)}`);
    if (!response.ok) throw new Error('Failed to fetch number of records');
    const data = await response.json();
    return data.records || [];
}

async function fetchValueCounts(db, collection, key) {
    const response = await fetch(`/mongo/show-value-counts?db=${encodeURIComponent(db)}&collection=${encodeURIComponent(collection)}&key=${encodeURIComponent(key)}`);
    if (!response.ok) throw new Error('Failed to fetch number of records');
    const data = await response.json();
    
    return data.counts || [];
}

// ====================== UI RENDER FUNCTIONS ======================

function createButton(label, cssClass, datasetProps = {}) {
    const btn = document.createElement('div');
    btn.textContent = label;
    btn.classList.add(cssClass);

    Object.entries(datasetProps).forEach(([key, value]) => {
        btn.dataset[key] = value;
    });

    return btn;
}

function showDBList(container, databases) {
    container.innerHTML = ""; // Clear existing list
    databases.forEach(dbName => {
        const dbButton = createButton(dbName, 'db-button', { dbName });
        container.appendChild(dbButton);
    });
}

function showCollections(container, dbName, collections) {
    container.innerHTML = "";
    
    collections.forEach(colName => {
        const colButton = createButton(colName, 'collection-button', { dbName, colName });
        container.appendChild(colButton);
    });
}
// ====================== EVENT HANDLERS ======================

function handleDBClick(e) {
    if (!e.target.classList.contains('db-button')) return;

    const dbName = e.target.dataset.dbName;
    const collectionContainer = document.getElementById('collections-list');

    fetchCollections(dbName)
        .then(collections => {
            showCollections(collectionContainer, dbName, collections);
        })
        .catch(err => console.error(err));

    toggleActiveState(e.target, '.db-button');
}
function handleCollectionClick(e) {
    if (!e.target.classList.contains('collection-button')) return;

    const dbName = e.target.dataset.dbName;
    const colName = e.target.dataset.colName;

    const recordCountDiv = document.getElementById('record-count');
    const recordContentDiv = document.getElementById('record-content');
    const recordValueCountsDiv = document.getElementById('record-value-counts');
    // Optional: Indicate loading state
    recordCountDiv.innerHTML = `<p>Loading count...</p>`;
    recordContentDiv.innerHTML = `<p>Loading records...</p>`;

    fetchNumRecords(dbName, colName)
        .then(count => {
            recordCountDiv.innerHTML = `<p>Total Records: ${count}</p>`;
        })
        .catch(err => {
            console.error(err);
            recordCountDiv.innerHTML = `<p style="color:red;">Failed to fetch record count</p>`;
        });
    fetchValueCounts(dbName, colName, "title")
        .then(counts => {
            counts.forEach(key_count => {
                const to_show = key_count.join(' ')
                const div = document.createElement('div');
                div.classList.add('db-button')
                div.innerHTML = `${to_show}`;
                recordValueCountsDiv.appendChild(div);
            })
        
        })



    fetchFirstNRecords(dbName, colName)
        .then(records => {
        recordContentDiv.innerHTML = '';
        records.forEach(record => {
            const pre = document.createElement('pre');
            const code = document.createElement('code');
            code.classList.add('json');  // Apply JSON highlighting
            // Generate pretty JSON without extra escaping for quotes
            const formattedJson = JSON.stringify(record, null, 2);

            // Set as textContent (so it won't double-escape) and rely on highlight.js
            code.textContent = formattedJson;
            pre.appendChild(code);
            recordContentDiv.appendChild(pre);
            hljs.highlightElement(code);  // Apply highlighting
        });

        if (records.length === 0) {
            recordContentDiv.textContent = 'No records found.';
        }

        })
        .catch(err => {
            console.error(err);
            recordContentDiv.innerHTML = `<p style="color:red;">Failed to fetch records</p>`;
        });

    toggleActiveState(e.target, '.collection-button');
}

function toggleActiveState(target, selector) {
    const allButtons = document.querySelectorAll(selector);
    allButtons.forEach(btn => btn.classList.remove('active'));
    target.classList.add('active');
}

// ====================== INITIALIZATION ======================

document.addEventListener('DOMContentLoaded', () => {
    const dbListContainer = document.getElementById('db-list');
    const collectionListContainer = document.getElementById('collections-list');

    // Fetch and show databases
    fetchDatabases()
        .then(databases => showDBList(dbListContainer, databases))
        .catch(err => console.error(err));

    // Attach event listeners
    dbListContainer.addEventListener('click', handleDBClick);
    collectionListContainer.addEventListener('click', handleCollectionClick);
});
