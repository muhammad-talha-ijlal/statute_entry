-- Create statute table
CREATE TABLE statute (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    act_no TEXT UNIQUE,
    date DATE,
    preface TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create part table
CREATE TABLE part (
    id SERIAL PRIMARY KEY,
    statute_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    part_no TEXT,
    order_no INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_part_statute FOREIGN KEY (statute_id) REFERENCES statute(id) ON DELETE CASCADE,
    CONSTRAINT uq_part_statute_order UNIQUE (statute_id, order_no)
);

-- Create chapter table
CREATE TABLE chapter (
    id SERIAL PRIMARY KEY,
    part_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    chapter_no TEXT,
    order_no INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chapter_part FOREIGN KEY (part_id) REFERENCES part(id) ON DELETE CASCADE,
    CONSTRAINT uq_chapter_part_order UNIQUE (part_id, order_no)
);

-- Create set table
CREATE TABLE set (
    id SERIAL PRIMARY KEY,
    chapter_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    set_no TEXT,
    order_no INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_set_chapter FOREIGN KEY (chapter_id) REFERENCES chapter(id) ON DELETE CASCADE,
    CONSTRAINT uq_set_chapter_order UNIQUE (chapter_id, order_no)
);

-- Create section table
CREATE TABLE section (
    id SERIAL PRIMARY KEY,
    set_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    section_no TEXT,
    order_no INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_section_set FOREIGN KEY (set_id) REFERENCES set(id) ON DELETE CASCADE,
    CONSTRAINT uq_section_set_order UNIQUE (set_id, order_no)
);

-- Create subsection table
CREATE TABLE subsection (
    id SERIAL PRIMARY KEY,
    section_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    subsection_no TEXT,
    content TEXT NOT NULL,
    order_no INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_subsection_section FOREIGN KEY (section_id) REFERENCES section(id) ON DELETE CASCADE,
    CONSTRAINT uq_subsection_section_order UNIQUE (section_id, order_no)
);

CREATE TABLE annotation (
    id SERIAL PRIMARY KEY,
    no TEXT NOT NULL,
    page_no TEXT,
    statute_id INTEGER,
    footnote TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_annotation_statute FOREIGN KEY (statute_id) REFERENCES statute(id) ON DELETE CASCADE,
    CONSTRAINT uq_annotation_statute_no UNIQUE (statute_id, no)
);

-- Create schedule part table
CREATE TABLE sch_part (
    id SERIAL PRIMARY KEY,
    statute_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    part_no TEXT,
    order_no INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sch_part_statute FOREIGN KEY (statute_id) REFERENCES statute(id) ON DELETE CASCADE,
    CONSTRAINT uq_sch_part_statute_order UNIQUE (statute_id, order_no)
);

-- Create schedule chapter table
CREATE TABLE sch_chapter (
    id SERIAL PRIMARY KEY,
    sch_part_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    chapter_no TEXT,
    order_no INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sch_chapter_part FOREIGN KEY (sch_part_id) REFERENCES sch_part(id) ON DELETE CASCADE,
    CONSTRAINT uq_sch_chapter_part_order UNIQUE (sch_part_id, order_no)
);

-- Create schedule set table
CREATE TABLE sch_set (
    id SERIAL PRIMARY KEY,
    sch_chapter_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    set_no TEXT,
    order_no INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sch_set_chapter FOREIGN KEY (sch_chapter_id) REFERENCES sch_chapter(id) ON DELETE CASCADE,
    CONSTRAINT uq_sch_set_chapter_order UNIQUE (sch_chapter_id, order_no)
);

-- Create schedule section table
CREATE TABLE sch_section (
    id SERIAL PRIMARY KEY,
    sch_set_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    section_no TEXT,
    order_no INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sch_section_set FOREIGN KEY (sch_set_id) REFERENCES sch_set(id) ON DELETE CASCADE,
    CONSTRAINT uq_sch_section_set_order UNIQUE (sch_set_id, order_no)
);

-- Create schedule subsection table
CREATE TABLE sch_subsection (
    id SERIAL PRIMARY KEY,
    sch_section_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    subsection_no TEXT,
    content TEXT NOT NULL,
    order_no INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sch_subsection_section FOREIGN KEY (sch_section_id) REFERENCES sch_section(id) ON DELETE CASCADE,
    CONSTRAINT uq_sch_subsection_section_order UNIQUE (sch_section_id, order_no)
);
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE "log" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id),
    table_name TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_part_statute_id ON part(statute_id);
CREATE INDEX idx_chapter_part_id ON chapter(part_id);
CREATE INDEX idx_set_chapter_id ON set(chapter_id);
CREATE INDEX idx_section_set_id ON section(set_id);
CREATE INDEX idx_subsection_section_id ON subsection(section_id);
CREATE INDEX idx_sch_part_statute_id ON sch_part(statute_id);
CREATE INDEX idx_sch_chapter_part_id ON sch_chapter(sch_part_id);
CREATE INDEX idx_sch_set_chapter_id ON sch_set(sch_chapter_id);
CREATE INDEX idx_sch_section_set_id ON sch_section(sch_set_id);
CREATE INDEX idx_sch_subsection_section_id ON sch_subsection(sch_section_id);