function showDBList (dbListContainer, data){
    data.databases.forEach(dbName => {
        const dbItem = document.createElement('div');
        dbItem.textContent = dbName;
        dbItem.classList.add('db-button');
        dbItem.dataset.dbName = dbName;
        // Click event
        dbItem.addEventListener('click', () => {
            dbItem.classList.toggle('active');
        });

        dbListContainer.appendChild(dbItem);
    });

}

fetch('/mongo/list-databases')
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log("Databases:", data.databases);
        const dbListContainer = document.getElementById('db-list');
        showDBList(dbListContainer, data);
    })
    .catch(error => {
        console.error('Error fetching database list:', error);
    });

async function fetchCollections(dbName) {
    try {
        const response = await fetch(`/mongo/list-collections?db=${encodeURIComponent(dbName)}`);
        if (!response.ok) throw new Error("Network error");

        const data = await response.json();
        console.log(`Collections in ${dbName}:`, data.collections);
        return data.collections || [];
    } catch (err) {
        console.error(err);
        return [];
    }
}
const dbListContainer = document.getElementById('db-list');

dbListContainer.addEventListener('click', async (e) => {
    if (e.target.classList.contains('db-button')) {
        const dbName = e.target.dataset.dbName;
        const collectionListContainer = document.getElementById('collections-list');

        const collections = await fetchCollections(dbName);
        console.log("Fetched Collections:", collections);
        /*collectionListContainer.innerHTML = `Collections: ${dbName}`;
        */
        collections.forEach(colName => {
                const colItem = document.createElement('div');
                colItem.textContent = colName;
                colItem.classList.add('db-button');
                // Click event
                colItem.addEventListener('click', async () => {
                    console.log(`Clicked: ${dbName}`);
                    colItem.classList.toggle('active');
                    const num_records = await fetch_num_records(dbName, colName)
                    console.log("Num records in :", dbName, colName, num_records);
                });

                collectionListContainer.appendChild(colItem);
            });
    }
});

const collection_container = document.getElementById('collections-list');

collection_container.addEventListener('click', (e) => {
    if (e.target.classList.contains('db-button')) {
        const allItems = collection_container.querySelectorAll('.db-button');
        allItems.forEach(item => item.classList.remove('active'));
        e.target.classList.add('active');
    }
});

async function fetch_num_records(db, collection) {
    const response = await fetch(`/mongo/num-records-in-collection?db=${encodeURIComponent(db)}&collection=${encodeURIComponent(collection)}`);
    
    if (!response.ok) {
        console.error('Failed to fetch number of records');
        return 0;
    }

    const data = await response.json();
    console.log('Num records:', data.num_records);
    
    return data.num_records || 0;
}
