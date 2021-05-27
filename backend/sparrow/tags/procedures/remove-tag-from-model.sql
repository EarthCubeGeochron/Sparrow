/*
SQL DELETE to remove a tag from a data model
*/

DELETE FROM :jointable WHERE :model_id_column = :model_id AND tag_id = :tag_id;