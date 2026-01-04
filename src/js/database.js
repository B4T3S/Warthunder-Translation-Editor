import initSqlJs from "sql.js";

export default class Database {
  constructor() {
    initSqlJs({
      locateFile: (file) => `https://sql.js.org/dist/${file}`,
    }).then((SQL) => {
      console.log("Initializing DB!");
      this.db = new SQL.Database();

      this.db.run(`
        CREATE TABLE translations (
          filename TEXT,
          ID_readonly_noverify TEXT,
          English TEXT,
          French TEXT,
          Italian TEXT,
          German TEXT,
          Spanish TEXT,
          Russian TEXT,
          Polish TEXT,
          Czech TEXT,
          Turkish TEXT,
          Chinese TEXT,
          Japanese TEXT,
          Portuguese TEXT,
          Ukrainian TEXT,
          Serbian TEXT,
          Hungarian TEXT,
          Korean TEXT,
          Belarusian TEXT,
          Romanian TEXT,
          TChinese TEXT,
          HChinese TEXT,
          Vietnamese TEXT,
          Comments TEXT,
          max_chars TEXT
        );
    `);
      this.db.run(`
      CREATE TABLE changes (
        key TEXT PRIMARY KEY,
        lang TEXT,
        change TEXT
      );
    `);

      this.db.run(`
        CREATE UNIQUE INDEX changes_key ON changes(key);
      `);
    });
  }

  addTranslationFile(filename, dataArray, languages) {
    this.db.run("BEGIN TRANSACTION;");

    const stmt = this.db.prepare(
      "INSERT INTO translations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
    );

    try {
      for (const row of dataArray) {
        const values = [
          filename,
          row["<ID|readonly|noverify>"] ?? "",
          row["<English>"] ?? "",
          row["<French>"] ?? "",
          row["<Italian>"] ?? "",
          row["<German>"] ?? "",
          row["<Spanish>"] ?? "",
          row["<Russian>"] ?? "",
          row["<Polish>"] ?? "",
          row["<Czech>"] ?? "",
          row["<Turkish>"] ?? "",
          row["<Chinese>"] ?? "",
          row["<Japanese>"] ?? "",
          row["<Portuguese>"] ?? "",
          row["<Ukrainian>"] ?? "",
          row["<Serbian>"] ?? "",
          row["<Hungarian>"] ?? "",
          row["<Korean>"] ?? "",
          row["<Belarusian>"] ?? "",
          row["<Romanian>"] ?? "",
          row["<TChinese>"] ?? "",
          row["<HChinese>"] ?? "",
          row["<Vietnamese>"] ?? "",
          row["<Comments>"] ?? "",
          row["<max_chars>"] ?? "",
        ];

        stmt.run(values);
      }

      stmt.free();

      this.db.run("COMMIT;");
    } catch (ex) {
      console.error("CAUGHT ERROR", ex);
      this.db.run("ROLLBACK;");
    }
  }

  getPaginatedSearchResults(language, query, page = 0, pageSize = 15) {
    const where = query == "" ? "" : `WHERE ${language} LIKE "%${query}%"`;

    const result = this.db.exec(
      `SELECT ID_readonly_noverify, ${language} FROM translations ${where} LIMIT ${pageSize} OFFSET ${page * pageSize}`,
    );

    if (result[0] == undefined) return [];

    return result[0].values;
  }

  getPages(language, query, pageSize = 15) {
    const where = query == "" ? "" : `WHERE ${language} LIKE "%${query}%"`;
    const result = this.db.exec(
      `SELECT COUNT(${language}) FROM translations ${where};`,
    );

    if (result[0] == undefined) return 0;

    return Math.ceil(result[0].values[0] / pageSize);
  }

  addChange(language, key, newText) {
    const translationCmd = `UPDATE translations SET ${language} = '${newText.replaceAll("'", "''")}' WHERE ID_readonly_noverify = '${key}';`;
    const changeStatement = this.db.prepare(
      `REPLACE INTO changes (key, lang, change) VALUES (?, ?, ?)`,
    );
    this.db.run("BEGIN TRANSACTION;");
    try {
      this.db.exec(translationCmd);
      changeStatement.run([key, language, newText]);

      changeStatement.free();
      this.db.run("COMMIT;");
    } catch (ex) {
      this.db.run("ROLLBACK;");
      console.error(ex);
    }
  }

  getChangeCount() {
    const result = this.db.exec("SELECT COUNT(*) FROM changes;");

    return result[0].values[0];
  }

  getAllChanges() {
    const result = this.db.exec(
      "SELECT c.key, c.lang, c.change, t.filename FROM changes c JOIN translations t ON c.key = t.ID_readonly_noverify;",
    );

    if (result[0] == undefined) return [];

    return result[0].values;
  }
}
