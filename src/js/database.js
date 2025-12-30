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
          dirty INTEGER,
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
    });
  }

  addTranslationFile(filename, dataArray, languages) {
    this.db.run("BEGIN TRANSACTION;");

    const stmt = this.db.prepare(
      "INSERT INTO translations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
    );

    try {
      for (const row of dataArray) {
        const values = [
          filename,
          false,
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
    const cmd = `UPDATE translations SET ${language} = '${newText.replaceAll("'", "''")}', dirty = TRUE WHERE ID_readonly_noverify = '${key}';`;
    console.log(cmd);
    this.db.exec(cmd);
  }

  getChangeCount() {
    const result = this.db.exec(
      "SELECT COUNT(*) FROM translations WHERE dirty = TRUE;",
    );

    return result[0].values[0];
  }
}
