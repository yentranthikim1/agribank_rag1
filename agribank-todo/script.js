/* ============================================
   QUẢN LÝ CÔNG VIỆC - AGRIBANK
   JavaScript Logic
   Lưu dữ liệu tạm trong bộ nhớ (localStorage)
   ============================================ */

// ========== KHỞI TẠO BIẾN TOÀN CỤC ==========
let tasks = []; // Danh sách công việc
let currentFilter = 'all'; // Bộ lọc hiện tại
let editingTaskId = null; // ID công việc đang được chỉnh sửa

// ========== HÀM KHỞI ĐỘNG ỨNG DỤNG ==========
document.addEventListener('DOMContentLoaded', () => {
    // Tải dữ liệu từ localStorage
    loadTasksFromStorage();
    
    // Gắn sự kiện cho các nút
    attachEventListeners();
    
    // Hiển thị danh sách công việc
    renderTasks();
});

// ========== HÀM LƯU/TẢI DỮ LIỆU ==========
/**
 * Lưu danh sách công việc vào localStorage
 */
function saveTasksToStorage() {
    localStorage.setItem('agribank_tasks', JSON.stringify(tasks));
}

/**
 * Tải danh sách công việc từ localStorage
 */
function loadTasksFromStorage() {
    const stored = localStorage.getItem('agribank_tasks');
    if (stored) {
        tasks = JSON.parse(stored);
    } else {
        // Dữ liệu mẫu ban đầu
        tasks = [
            {
                id: 1,
                ten: 'Hoàn thành tài liệu dự án',
                nguoi_phu_trach: 'Hoàng Văn A',
                trang_thai: 'pending'
            },
            {
                id: 2,
                ten: 'Test ứng dụng quản lý công việc',
                nguoi_phu_trach: 'Trần Thị B',
                trang_thai: 'completed'
            }
        ];
        saveTasksToStorage();
    }
}

// ========== HÀM GẮN SỰ KIỆN ==========
/**
 * Gắn sự kiện cho các nút và input
 */
function attachEventListeners() {
    // Nút thêm công việc
    document.getElementById('addTaskBtn').addEventListener('click', handleAddTask);
    
    // Phím Enter trong input
    document.getElementById('taskName').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleAddTask();
    });
    
    document.getElementById('taskAssignee').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleAddTask();
    });
    
    // Nút lọc công việc
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', handleFilterChange);
    });
}

// ========== HÀM XỬ LÝ THÊM CÔNG VIỆC ==========
/**
 * Xử lý thêm công việc mới
 */
function handleAddTask() {
    const nameInput = document.getElementById('taskName');
    const assigneeInput = document.getElementById('taskAssignee');
    
    const name = nameInput.value.trim();
    const assignee = assigneeInput.value.trim();
    
    // Kiểm tra dữ liệu nhập vào
    if (!name || !assignee) {
        alert('⚠️ Vui lòng nhập đầy đủ tên công việc và người phụ trách!');
        return;
    }
    
    // Tạo công việc mới
    const newTask = {
        id: Date.now(), // Dùng timestamp làm ID duy nhất
        ten: name,
        nguoi_phu_trach: assignee,
        trang_thai: 'pending'
    };
    
    tasks.push(newTask);
    saveTasksToStorage();
    
    // Xóa dữ liệu input
    nameInput.value = '';
    assigneeInput.value = '';
    nameInput.focus();
    
    // Cập nhật hiển thị
    renderTasks();
}

// ========== HÀM XỬ LÝ LỌCÔNG VIỆC ==========
/**
 * Xử lý thay đổi bộ lọc
 */
function handleFilterChange(e) {
    const filterBtn = e.target;
    
    // Cập nhật nút active
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    filterBtn.classList.add('active');
    
    // Cập nhật bộ lọc hiện tại
    currentFilter = filterBtn.dataset.filter;
    
    // Cập nhật hiển thị
    renderTasks();
}

// ========== HÀM TOGGLE TRẠNG THÁI CÔNG VIỆC ==========
/**
 * Chuyển đổi trạng thái hoàn thành/chưa hoàn thành
 * @param {number} taskId - ID công việc
 */
function toggleTaskStatus(taskId) {
    const task = tasks.find(t => t.id === taskId);
    if (task) {
        task.trang_thai = task.trang_thai === 'pending' ? 'completed' : 'pending';
        saveTasksToStorage();
        renderTasks();
    }
}

// ========== HÀM XÓA CÔNG VIỆC ==========
/**
 * Xóa công việc theo ID
 * @param {number} taskId - ID công việc
 */
function deleteTask(taskId) {
    if (confirm('❓ Bạn chắc chắn muốn xóa công việc này không?')) {
        tasks = tasks.filter(t => t.id !== taskId);
        saveTasksToStorage();
        renderTasks();
    }
}

// ========== HÀM CHỈNH SỬA CÔNG VIỆC ==========
/**
 * Mở modal để chỉnh sửa công việc
 * @param {number} taskId - ID công việc
 */
function editTask(taskId) {
    const task = tasks.find(t => t.id === taskId);
    if (task) {
        editingTaskId = taskId;
        const nameInput = document.getElementById('taskName');
        const assigneeInput = document.getElementById('taskAssignee');
        
        nameInput.value = task.ten;
        assigneeInput.value = task.nguoi_phu_trach;
        
        // Thay đổi text nút thêm thành cập nhật
        const addBtn = document.getElementById('addTaskBtn');
        addBtn.textContent = '✏️ Cập nhật Công việc';
        addBtn.onclick = handleUpdateTask;
        
        nameInput.focus();
    }
}

/**
 * Xử lý cập nhật công việc
 */
function handleUpdateTask() {
    const nameInput = document.getElementById('taskName');
    const assigneeInput = document.getElementById('taskAssignee');
    
    const name = nameInput.value.trim();
    const assignee = assigneeInput.value.trim();
    
    if (!name || !assignee) {
        alert('⚠️ Vui lòng nhập đầy đủ tên công việc và người phụ trách!');
        return;
    }
    
    const task = tasks.find(t => t.id === editingTaskId);
    if (task) {
        task.ten = name;
        task.nguoi_phu_trach = assignee;
        saveTasksToStorage();
    }
    
    // Đặt lại trạng thái
    resetFormState();
    renderTasks();
}

/**
 * Đặt lại trạng thái form
 */
function resetFormState() {
    editingTaskId = null;
    document.getElementById('taskName').value = '';
    document.getElementById('taskAssignee').value = '';
    const addBtn = document.getElementById('addTaskBtn');
    addBtn.textContent = '➕ Thêm Công việc';
    addBtn.onclick = handleAddTask;
}

// ========== HÀM LỌC VÀ HIỂN THỊ CÔNG VIỆC ==========
/**
 * Lọc danh sách công việc theo trạng thái
 * @returns {Array} - Danh sách công việc đã lọc
 */
function getFilteredTasks() {
    if (currentFilter === 'all') {
        return tasks;
    } else if (currentFilter === 'pending') {
        return tasks.filter(t => t.trang_thai === 'pending');
    } else if (currentFilter === 'completed') {
        return tasks.filter(t => t.trang_thai === 'completed');
    }
    return tasks;
}

/**
 * Hiển thị danh sách công việc lên trang
 */
function renderTasks() {
    const tasksList = document.getElementById('tasksList');
    const filteredTasks = getFilteredTasks();
    
    // Cập nhật số lượng công việc
    document.getElementById('taskCount').textContent = tasks.length;
    
    // Xóa danh sách cũ
    tasksList.innerHTML = '';
    
    // Kiểm tra danh sách trống
    if (filteredTasks.length === 0) {
        const emptyMsg = document.createElement('p');
        emptyMsg.className = 'empty-message';
        
        if (currentFilter === 'completed') {
            emptyMsg.textContent = '✓ Tuyệt vời! Không có công việc chưa hoàn thành.';
        } else if (currentFilter === 'pending') {
            emptyMsg.textContent = '✓ Tất cả công việc đang làm đã hoàn thành!';
        } else {
            emptyMsg.textContent = 'Chưa có công việc nào. Hãy thêm công việc mới!';
        }
        
        tasksList.appendChild(emptyMsg);
        return;
    }
    
    // Render từng công việc
    filteredTasks.forEach(task => {
        const taskElement = createTaskElement(task);
        tasksList.appendChild(taskElement);
    });
}

/**
 * Tạo phần tử HTML cho một công việc
 * @param {Object} task - Đối tượng công việc
 * @returns {HTMLElement} - Phần tử HTML
 */
function createTaskElement(task) {
    const taskItem = document.createElement('div');
    taskItem.className = `task-item ${task.trang_thai === 'completed' ? 'completed' : ''}`;
    taskItem.id = `task-${task.id}`;
    
    // Checkbox
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'task-checkbox';
    checkbox.checked = task.trang_thai === 'completed';
    checkbox.addEventListener('change', () => toggleTaskStatus(task.id));
    
    // Nội dung công việc
    const content = document.createElement('div');
    content.className = 'task-content';
    
    const name = document.createElement('div');
    name.className = 'task-name';
    name.textContent = task.ten;
    
    const assignee = document.createElement('div');
    assignee.className = 'task-assignee';
    assignee.textContent = task.nguoi_phu_trach;
    
    const status = document.createElement('div');
    status.className = `task-status status-${task.trang_thai}`;
    status.textContent = task.trang_thai === 'pending' ? '⏳ Đang làm' : '✓ Hoàn thành';
    
    content.appendChild(name);
    content.appendChild(assignee);
    content.appendChild(status);
    
    // Nút hành động
    const actions = document.createElement('div');
    actions.className = 'task-actions';
    
    const editBtn = document.createElement('button');
    editBtn.className = 'btn-small btn-edit';
    editBtn.textContent = '✏️ Sửa';
    editBtn.addEventListener('click', () => editTask(task.id));
    
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'btn-small btn-delete';
    deleteBtn.textContent = '🗑️ Xóa';
    deleteBtn.addEventListener('click', () => deleteTask(task.id));
    
    actions.appendChild(editBtn);
    actions.appendChild(deleteBtn);
    
    // Ghép lại thành một phần tử
    taskItem.appendChild(checkbox);
    taskItem.appendChild(content);
    taskItem.appendChild(actions);
    
    return taskItem;
}
