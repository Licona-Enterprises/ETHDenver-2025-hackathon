import { NextResponse } from "next/server";
import { MongoClient, ObjectId } from "mongodb";
import { MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION_PORTFOLIO } from "../../../constants/consts";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const agentId = searchParams.get("agentId");

  if (!agentId) {
    return NextResponse.json({ error: "agentId is required" }, { status: 400 });
  }

  let objectId;
  try {
    objectId = new ObjectId(agentId); // Convert string to ObjectId
  } catch (error) {
    return NextResponse.json({ error: "Invalid agentId format" }, { status: 400 });
  }

  const client = new MongoClient(MONGODB_URI);

  try {
    await client.connect();
    const db = client.db(MONGODB_DB);
    const collection = db.collection(MONGODB_COLLECTION_PORTFOLIO); // Adjust collection name

    // Fetch the portfolio using ObjectId
    const portfolio = await collection.findOne({ agentId: objectId });

    if (!portfolio) {
      return NextResponse.json({ error: "Portfolio not found" }, { status: 404 });
    }

    return NextResponse.json(portfolio, {
      headers: { "Cache-Control": "no-store" },
    });
  } catch (error) {
    console.error("Error fetching agent portfolio:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  } finally {
    await client.close();
  }
}
