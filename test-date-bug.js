// Test the date parsing bug
const dateStr = "2025-08-18";
const predDate = new Date(dateStr);
console.log("Date string:", dateStr);
console.log("Parsed date:", predDate);
console.log("Day of week:", predDate.getDay());
console.log("Is Monday (1)?:", predDate.getDay() === 1);
console.log("Shows as weekend?:", predDate.getDay() === 0 || predDate.getDay() === 6);

// Try with explicit time
const predDate2 = new Date(dateStr + "T00:00:00");
console.log("\nWith T00:00:00:");
console.log("Parsed date:", predDate2);
console.log("Day of week:", predDate2.getDay());
console.log("Shows as weekend?:", predDate2.getDay() === 0 || predDate2.getDay() === 6);
