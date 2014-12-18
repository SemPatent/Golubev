CREATE TABLE documents (
    id bigint primary key,
    body varchar(254),                              -- body lang
    p_number text,                                  -- doc-number
    p_date date,                                    -- date
    language varchar(254),                          -- lang
    title text,                                     -- title
    ipc_class varchar(254),                         -- part of classification
    ipc_classification varchar(254),                -- classification
    title_en text,                                  -- title_en
    kind_code varchar(254),                         -- kind
    applicants text[],                              -- applicant
    owners text[],
    application_number bigint,
    application_date date,
    application_body varchar(254),
    priority_number bigint,
    priority_body bigint,
    priority_date date,
    disclaimer_date date
);

CREATE TABLE citations (
    id bigint primary key,
    patent_id bigint references documents(id),
    cited_patent_body varchar(254),
    cited_patent_number bigint,
    cited_patent_kind varchar(254),
    by_examiner boolean,
    cited_patent_id bigint
);

CREATE TABLE query_requests (
    id bigint primary key,                          -- id key
    patent_abstract text,                           -- abstract
    description text,                               -- description
    claims text,                                    -- claims
    ipc_class varchar(254),                         -- classification
    body varchar(254),                              -- lang
    created_at date,                                -- date-publ
    relevant_ids text[]                             -- citation        
);

CREATE TABLE should_accept_log (
    id bigint primary key,                          -- id key
    query bigint references query_requests(id),     -- reference    
    patent_id bigint references documents(id),      -- reference
    is_should_accept boolean default true,
    alpha_coeff double precision,                   -- alpha
    beta_key double precision,                      -- beta key
    beta_coeff double precision[]                   -- beta coeff
);
