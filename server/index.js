const express = require("express");

const PORT = process.env.PORT || 3001;

const app = express();
app.use(express.json());
app.use(express.urlencoded({extended: true}));

const fs = require("fs");

app.get("/api", (req, res) => {
  const stateData = JSON.parse(fs.readFileSync("data.json"));
  console.log(stateData);
  res.json(stateData);
});

app.post("/api", (req, res) => {
  console.log(req.body);
  fs.writeFileSync("data.json", JSON.stringify(req.body));
  res.sendStatus(200);
})

app.listen(PORT, () => {
  console.log(`Server listening on ${PORT}`);
});
