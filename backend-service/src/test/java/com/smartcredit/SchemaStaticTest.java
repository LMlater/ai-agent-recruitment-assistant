package com.smartcredit;

import org.junit.jupiter.api.Test;

import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertTrue;

class SchemaStaticTest {

    @Test
    void schemaContainsMaterialUpdateRecordTable() throws Exception {
        String schema = Files.readString(Path.of("src/main/resources/db/schema.sql"));

        assertTrue(schema.contains("create table if not exists material_update_record"));
        assertTrue(schema.contains("application_id bigint not null"));
        assertTrue(schema.contains("operator_id bigint not null"));
        assertTrue(schema.contains("material_summary text not null"));
        assertTrue(schema.contains("idx_material_application"));
    }
}
