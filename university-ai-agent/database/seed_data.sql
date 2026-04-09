-- ============================================
-- GIFT University - Seed Data
-- ============================================

-- Programs Data
INSERT INTO programs (name, degree_type, category, duration, eligibility, description) VALUES
-- Associate Degrees
('AD Computer Science', 'AD', 'associate', '2 years', 'Intermediate / FA / FSc', 'Learn programming, algorithms, and computer systems'),
('AD Accounting and Finance', 'AD', 'associate', '2 years', 'Intermediate / FA / FSc', 'Foundation in financial principles and accounting practices'),
('AD Business Innovation & Entrepreneurship', 'AD', 'associate', '2 years', 'Intermediate / FA / FSc', 'Skills to launch and manage innovative businesses'),
('AD Mass Communication & Media Studies', 'AD', 'associate', '2 years', 'Intermediate / FA / FSc', 'Media production, journalism, and public relations'),
('AD Clinical Psychology', 'AD', 'associate', '2 years', 'Intermediate / FA / FSc', 'Foundations of mental health and psychological assessment'),
('AD Management Sciences', 'AD', 'associate', '2 years', 'Intermediate / FA / FSc', 'Organizational behavior, strategic planning, and leadership'),

-- BS Programs (After 12 Years)
('BS Computer Science', 'BS', 'undergraduate', '4 years', 'FSc / ICS / A-Levels (50% min)', 'Advanced study of programming, software engineering, and computer systems'),
('BS Software Engineering', 'BS', 'undergraduate', '4 years', 'FSc / ICS / A-Levels (50% min)', 'Software development methodologies, project management, and coding'),
('BS Data Science', 'BS', 'undergraduate', '4 years', 'FSc / ICS / A-Levels (50% min)', 'Analyze and interpret complex data using statistical and computational methods'),
('BS Artificial Intelligence', 'BS', 'undergraduate', '4 years', 'FSc / ICS / A-Levels (50% min)', 'Mathematics and AI technologies for data science and robotics'),
('BS Business Administration (BBA)', 'BS', 'undergraduate', '4 years', 'Intermediate (45% min)', 'Comprehensive business management and leadership program'),
('BS Accounting and Finance', 'BS', 'undergraduate', '4 years', 'Intermediate (45% min)', 'Financial reporting, auditing, and corporate finance'),
('BS Mass Communication & Media Studies', 'BS', 'undergraduate', '4 years', 'Intermediate (45% min)', 'Media production, journalism, and communication theory'),
('BS Psychology', 'BS', 'undergraduate', '4 years', 'Intermediate (45% min)', 'Human behavior, cognition, and psychological research'),
('BS English', 'BS', 'undergraduate', '4 years', 'Intermediate (45% min)', 'Advanced language skills and literature from various cultures'),
('BS Islamic Studies', 'BS', 'undergraduate', '4 years', 'Intermediate (45% min)', 'Islamic theology, jurisprudence, and contemporary issues'),
('BS Mathematics', 'BS', 'undergraduate', '4 years', 'FSc Pre-Engineering / ICS (50% min)', 'Advanced mathematical concepts and computational mathematics'),
('BS Financial Technology (FinTech)', 'BS', 'undergraduate', '4 years', 'Intermediate (45% min)', 'Finance merged with FinTech and global certifications'),
('BS Islamic Banking and Digital Finance', 'BS', 'undergraduate', '4 years', 'Intermediate (45% min)', 'Shariah principles with modern fintech for ethical finance'),
('BDes Graphic Design', 'BDes', 'undergraduate', '4 years', 'Intermediate (45% min)', 'Visual communication for print and digital media'),
('BCom (Hons)', 'BCom', 'undergraduate', '4 years', 'Intermediate (45% min)', 'Accounting, economics, and business law'),

-- Postgraduate Programs
('MBA', 'MBA', 'postgraduate', '2 years', 'Bachelor degree (16 years education)', 'Business management, finance, and strategic planning'),
('MS Computer Science', 'MS', 'postgraduate', '2 years', 'BS Computer Science or related (16 years)', 'Advanced algorithms, AI, and software engineering'),
('MPhil Management Sciences', 'MPhil', 'postgraduate', '2 years', 'Bachelor degree (16 years education)', 'Research in management and organizational behavior'),
('MPhil English', 'MPhil', 'postgraduate', '2 years', 'BS English or related (16 years)', 'Literature, linguistics, and research'),
('MPhil Psychology', 'MPhil', 'postgraduate', '2 years', 'BS Psychology (16 years)', 'Advanced research and professional expertise in psychology'),
('MS Clinical Psychology', 'MS', 'postgraduate', '2 years', 'BS Psychology (16 years)', 'Clinical, diagnostic, and therapeutic expertise'),
('PhD Computer Science', 'PhD', 'postgraduate', '3-5 years', 'MS/MPhil Computer Science', 'Original research contributions to computer science');

-- Fee Structure
INSERT INTO fee_structure (program_category, fee_per_semester, annual_fee, admission_fee, note) VALUES
('associate', 35000, 70000, 15000, 'AD programs - 2 year duration'),
('undergraduate', 55000, 110000, 20000, 'BS/BBA/BCom/BDes programs - 4 year duration'),
('postgraduate', 60000, 120000, 25000, 'MBA/MS/MPhil programs - 2 year duration'),
('phd', 75000, 150000, 30000, 'PhD programs - 3 to 5 year duration');

-- Admission Requirements
INSERT INTO admission_requirements (program_category, min_percentage, required_documents, entry_test_required, entry_test_info, note) VALUES
('associate', 45, '["Matric Certificate", "Intermediate Certificate", "CNIC/B-Form", "4 Passport Photos", "Character Certificate"]', false, NULL, 'AD programs require Intermediate or equivalent'),
('undergraduate', 50, '["Matric Certificate", "Intermediate Certificate", "CNIC/B-Form", "4 Passport Photos", "Character Certificate", "Migration Certificate (if applicable)"]', false, 'Entry test may be required for some programs', 'FSc/ICS required for CS/IT programs, Intermediate for others'),
('postgraduate', 45, '["Bachelor Degree", "Transcripts", "CNIC", "4 Passport Photos", "Character Certificate", "Experience Letter (if applicable)"]', false, NULL, '16 years of education required for MS/MBA/MPhil'),
('phd', 60, '["MS/MPhil Degree", "Transcripts", "CNIC", "Research Proposal", "2 Reference Letters", "Publications (if any)"]', true, 'GAT/NTS test required with minimum 50% score', '18 years of education required');

-- Admission Dates
INSERT INTO admission_dates (semester, year, admission_start, admission_end, classes_start, is_active) VALUES
('Fall', 2025, '2025-07-01', '2025-08-31', '2025-09-15', true),
('Spring', 2026, '2025-12-01', '2026-01-31', '2026-02-15', false);

-- FAQs
INSERT INTO faqs (question, answer, category) VALUES
('GIFT University mein admission kaise lein?', 'GIFT University mein admission ke liye pehle online application form fill karein gift.edu.pk pe, phir required documents submit karein, admission fee pay karein aur merit list ka wait karein.', 'admission'),
('Kaunse documents chahiye admission ke liye?', 'Matric aur Intermediate certificates, CNIC ya B-Form, 4 passport size photos, aur character certificate chahiye. Postgraduate ke liye Bachelor degree aur transcripts bhi.', 'admission'),
('BS programs ki fees kitni hai?', 'BS programs ki fee approximately 55,000 rupees per semester hai. Admission fee 20,000 rupees alag se hai. Annual fee approximately 1,10,000 rupees banti hai.', 'fee'),
('Scholarship milti hai GIFT mein?', 'Haan, GIFT Advantage Program (GAP) ke through scholarships milti hain. Merit based, need based, aur sports scholarships available hain. Admission ke waqt apply kar sakte hain.', 'scholarship'),
('CS ya IT ke liye kya eligibility hai?', 'BS Computer Science ya Software Engineering ke liye FSc Pre-Engineering ya ICS mein minimum 50% marks chahiye. A-Levels bhi acceptable hai.', 'admission'),
('GIFT University ka address kya hai?', 'GIFT University, Gujranwala, Punjab, Pakistan. Main campus Gujranwala mein hai.', 'contact'),
('Hostel facility hai GIFT mein?', 'GIFT University mein hostel facility available hai. Boys aur girls ke liye alag hostels hain. Admission office se hostel availability confirm karein.', 'hostel'),
('MBA ke liye kya requirements hain?', 'MBA ke liye 16 years ki education chahiye yaani Bachelor degree. Minimum 45% marks required hain. 2 saal ka program hai.', 'admission'),
('Fall 2025 admission kab tak hain?', 'Fall 2025 admissions July 2025 se August 2025 tak open hain. Classes September 2025 mein start hongi.', 'admission'),
('Entry test hota hai GIFT mein?', 'Zyada tar undergraduate programs mein entry test nahi hota, merit based admission hota hai. PhD ke liye GAT/NTS test zaroori hai.', 'admission'),
('Transport facility hai?', 'GIFT University transport facility provide karti hai Gujranwala aur surrounding areas ke liye. Transport office se routes aur fees confirm karein.', 'transport'),
('AD program kya hota hai?', 'Associate Degree 2 saal ka program hota hai Intermediate ke baad. Yeh BS mein convert bhi ho sakta hai. Computer Science, Business, Psychology wagera mein available hai.', 'admission');

-- Contact Info
INSERT INTO contact_info (department, phone, email, location, timings) VALUES
('Admissions Office', '055-111-GIFT-00', 'admissions@gift.edu.pk', 'Main Campus, Gujranwala', 'Monday to Friday: 9am - 5pm'),
('Helpdesk / Inquiry', '055-111-GIFT-00', 'info@gift.edu.pk', 'Main Campus, Gujranwala', 'Monday to Friday: 9am - 5pm'),
('Finance / Fee Department', '055-111-GIFT-00', 'finance@gift.edu.pk', 'Main Campus, Gujranwala', 'Monday to Friday: 9am - 4pm'),
('Hostel Office', '055-111-GIFT-00', 'hostel@gift.edu.pk', 'Main Campus, Gujranwala', 'Monday to Saturday: 9am - 6pm');
