// app/api/agent/route.ts (if using App Router)
import { NextResponse } from "next/server";
import { MongoClient } from "mongodb";
import { MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION } from "../../../constants/consts";

const uri = MONGODB_URI as string; // MongoDB URI
const dbName = MONGODB_DB as string; // MongoDB database name
const collectionName = MONGODB_COLLECTION as string; // MongoDB collection name

const client = new MongoClient(uri);
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    await client.connect();
    const db = client.db(dbName);
    const collection = db.collection(collectionName);

    // Fetch agents from the database
    const agents = await collection.find({}).toArray();

    await client.close();

    return NextResponse.json(agents, {
      headers: { "Cache-Control": "no-store" },
    });
  } catch (error) {
    console.error("Error fetching agents:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
