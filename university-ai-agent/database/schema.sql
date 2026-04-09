-- ============================================
-- GIFT University AI Agent - Database Schema
-- ============================================

-- Programs Table
CREATE TABLE IF NOT EXISTS programs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    degree_type VARCHAR(50) NOT NULL, -- BS, MPhil, MBA, PhD, AD, BDes, BCom
    category VARCHAR(50) NOT NULL,    -- undergraduate, postgraduate, associate
    duration VARCHAR(20),             -- 4 years, 2 years etc
    eligibility VARCHAR(200),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fee Structure Table
CREATE TABLE IF NOT EXISTS fee_structure (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    program_category VARCHAR(50) NOT NULL, -- undergraduate, postgraduate, associate
    fee_per_semester INTEGER NOT NULL,
    annual_fee INTEGER NOT NULL,
    admission_fee INTEGER DEFAULT 0,
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Admission Requirements Table
CREATE TABLE IF NOT EXISTS admission_requirements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    program_category VARCHAR(50) NOT NULL,
    min_percentage INTEGER,
    required_documents JSONB DEFAULT '[]',
    entry_test_required BOOLEAN DEFAULT FALSE,
    entry_test_info TEXT,
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Important Dates Table
CREATE TABLE IF NOT EXISTS admission_dates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    semester VARCHAR(20) NOT NULL,   -- Fall, Spring
    year INTEGER NOT NULL,
    admission_start DATE,
    admission_end DATE,
    classes_start DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- FAQs Table
CREATE TABLE IF NOT EXISTS faqs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(50),  -- admission, fee, hostel, transport, scholarship
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Contact Info Table
CREATE TABLE IF NOT EXISTS contact_info (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    department VARCHAR(100) NOT NULL,
    phone VARCHAR(50),
    email VARCHAR(100),
    location VARCHAR(200),
    timings VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Call Logs Table
CREATE TABLE IF NOT EXISTS call_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(50),
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    intent VARCHAR(50),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Sessions Table
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    session_data JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
