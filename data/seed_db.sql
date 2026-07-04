CREATE TABLE IF NOT EXISTS revenue (
    quarter TEXT NOT NULL,
    department TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'VND'
);

CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    role TEXT NOT NULL,
    salary REAL NOT NULL,
    start_date TEXT NOT NULL
);

-- Revenue data (in billion VND, stored as raw number)
INSERT INTO revenue (quarter, department, amount, currency) VALUES
('Q1-2025', 'engineering', 24000000000, 'VND'),
('Q1-2025', 'consulting', 10000000000, 'VND'),
('Q1-2025', 'support', 4000000000, 'VND'),
('Q2-2025', 'engineering', 26000000000, 'VND'),
('Q2-2025', 'consulting', 11000000000, 'VND'),
('Q2-2025', 'support', 4500000000, 'VND'),
('Q3-2025', 'engineering', 28000000000, 'VND'),
('Q3-2025', 'consulting', 12000000000, 'VND'),
('Q3-2025', 'support', 5000000000, 'VND'),
('Q4-2025', 'engineering', 30000000000, 'VND'),
('Q4-2025', 'consulting', 13000000000, 'VND'),
('Q4-2025', 'support', 5500000000, 'VND');

-- Employee data
INSERT INTO employees (name, department, role, salary, start_date) VALUES
('Nguyen Van An', 'engineering', 'Senior Engineer', 45000000, '2021-03-15'),
('Tran Thi Binh', 'engineering', 'Lead Engineer', 65000000, '2019-08-01'),
('Le Hoang Cuong', 'engineering', 'Junior Engineer', 18000000, '2024-06-01'),
('Pham Minh Duc', 'engineering', 'Senior Engineer', 50000000, '2020-11-20'),
('Vo Thanh Em', 'engineering', 'Mid Engineer', 30000000, '2023-01-10'),
('Hoang Thi Phuong', 'engineering', 'DevOps Engineer', 42000000, '2022-04-05'),
('Nguyen Duc Giang', 'engineering', 'Junior Engineer', 16000000, '2025-01-15'),
('Bui Van Hai', 'engineering', 'Senior Engineer', 52000000, '2020-07-01'),
('Dang Thi Yen', 'engineering', 'QA Engineer', 28000000, '2023-05-20'),
('Tran Van Khanh', 'engineering', 'Tech Lead', 72000000, '2018-09-01'),
('Nguyen Thi Lan', 'hr', 'HR Manager', 48000000, '2020-02-01'),
('Pham Van Minh', 'hr', 'HR Specialist', 25000000, '2023-04-15'),
('Le Thi Nga', 'hr', 'Recruiter', 22000000, '2024-01-10'),
('Vo Van Oanh', 'hr', 'Training Coordinator', 20000000, '2024-03-01'),
('Tran Quoc Phong', 'finance', 'CFO', 95000000, '2018-01-15'),
('Nguyen Thi Quyen', 'finance', 'Senior Accountant', 38000000, '2021-06-01'),
('Le Van Rong', 'finance', 'Accountant', 22000000, '2023-08-15'),
('Pham Thi Sen', 'finance', 'Financial Analyst', 32000000, '2022-02-01'),
('Hoang Van Tuan', 'legal', 'Legal Director', 85000000, '2019-03-01'),
('Nguyen Thi Uyen', 'legal', 'Legal Counsel', 45000000, '2021-09-15'),
('Tran Van Vinh', 'legal', 'Compliance Officer', 40000000, '2022-07-01'),
('Le Thi Xuan', 'legal', 'Paralegal', 18000000, '2024-05-01'),
('Pham Duc Yen', 'engineering', 'ML Engineer', 55000000, '2021-01-20'),
('Bui Thi Anh', 'engineering', 'Frontend Developer', 32000000, '2023-03-15'),
('Dang Van Binh', 'engineering', 'Backend Developer', 38000000, '2022-08-01'),
('Vo Thi Cam', 'finance', 'Accounts Payable', 20000000, '2024-02-01'),
('Hoang Van Dat', 'engineering', 'SRE Engineer', 48000000, '2021-05-10'),
('Nguyen Thi Hoa', 'hr', 'Compensation Analyst', 30000000, '2022-11-01');
