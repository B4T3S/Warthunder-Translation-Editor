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
    const result = this.db.exec(
      `SELECT ID_readonly_noverify, ${language} FROM translations LIMIT ${pageSize} OFFSET ${page * pageSize}`,
    );

    return result[0].values;
  }
}
