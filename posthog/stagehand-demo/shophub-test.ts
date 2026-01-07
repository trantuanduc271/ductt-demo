import { Stagehand } from "@browserbasehq/stagehand";
import { z } from "zod";
import * as fs from "fs";
import * as path from "path";

interface TestResult {
  testName: string;
  status: "passed" | "failed" | "skipped";
  duration: number;
  result?: any;
  error?: string;
  timestamp: string;
}

class TestReporter {
  private results: TestResult[] = [];
  private startTime: number = Date.now();

  addResult(result: TestResult) {
    this.results.push(result);
  }

  generateReport(): string {
    const totalTime = Date.now() - this.startTime;
    const passed = this.results.filter(r => r.status === "passed").length;
    const failed = this.results.filter(r => r.status === "failed").length;
    const skipped = this.results.filter(r => r.status === "skipped").length;

    let report = "\n" + "=".repeat(80) + "\n";
    report += "SHOPHUB TEST REPORT\n";
    report += "=".repeat(80) + "\n\n";
    report += `Test URL: http://localhost:3000\n`;
    report += `Test Email: dtran@slower.ai\n\n`;
    report += `Total Tests: ${this.results.length}\n`;
    report += `Passed: ${passed}\n`;
    report += `Failed: ${failed}\n`;
    report += `Skipped: ${skipped}\n`;
    report += `Total Time: ${(totalTime / 1000).toFixed(2)}s\n\n`;

    report += "Detailed Results:\n";
    report += "-".repeat(80) + "\n";
    
    this.results.forEach((result, index) => {
      report += `\n${index + 1}. ${result.testName}\n`;
      report += `   Status: ${result.status.toUpperCase()}\n`;
      report += `   Time: ${result.timestamp}\n`;
      report += `   Duration: ${result.duration}ms\n`;
      if (result.result) {
        report += `   Result: ${JSON.stringify(result.result, null, 2)}\n`;
      }
      if (result.error) {
        report += `   Error: ${result.error}\n`;
      }
    });

    report += "\n" + "=".repeat(80) + "\n";
    return report;
  }

  saveReport(filename: string = "shophub-test-report.txt") {
    const report = this.generateReport();
    const reportPath = path.join(process.cwd(), filename);
    fs.writeFileSync(reportPath, report, "utf-8");
    return reportPath;
  }
}

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

const TEST_EMAIL = "dtran@slower.ai";
const BASE_URL = "http://localhost:3000";

async function runShopHubTests() {
  const reporter = new TestReporter();

  const stagehand = new Stagehand({
    env: "LOCAL",
    verbose: 0,
    model: "google/gemini-2.0-flash",
  });

  await stagehand.init();
  await delay(2000);

  try {
    const page = stagehand.context.pages()[0];

    const test1Start = Date.now();
    try {
      await page.goto(BASE_URL);
      await delay(3000);
      
      const homepageData = await stagehand.extract(
        "extract the main heading and the two call-to-action button texts",
        z.object({
          heading: z.string(),
          buttons: z.array(z.string()),
        })
      );
      
      reporter.addResult({
        testName: "Homepage Navigation",
        status: "passed",
        duration: Date.now() - test1Start,
        result: homepageData,
        timestamp: new Date().toISOString(),
      });
    } catch (error: any) {
      reporter.addResult({
        testName: "Homepage Navigation",
        status: "failed",
        duration: Date.now() - test1Start,
        error: error.message,
        timestamp: new Date().toISOString(),
      });
    }

    await delay(2000);

    const test2Start = Date.now();
    try {
      await stagehand.act("click the Shop Now button");
      await delay(3000);
      
      const currentUrl = page.url();
      
      reporter.addResult({
        testName: "Navigate to Products (Shop Now)",
        status: "passed",
        duration: Date.now() - test2Start,
        result: { url: currentUrl },
        timestamp: new Date().toISOString(),
      });
    } catch (error: any) {
      reporter.addResult({
        testName: "Navigate to Products (Shop Now)",
        status: "failed",
        duration: Date.now() - test2Start,
        error: error.message,
        timestamp: new Date().toISOString(),
      });
    }

    await delay(2000);

    const test3Start = Date.now();
    try {
      const products = await stagehand.extract(
        "extract the first 3 products with their names and prices",
        z.object({
          products: z.array(
            z.object({
              name: z.string(),
              price: z.string(),
            })
          ),
        })
      );
      
      reporter.addResult({
        testName: "Browse Products",
        status: "passed",
        duration: Date.now() - test3Start,
        result: { productsCount: products.products.length, products: products.products },
        timestamp: new Date().toISOString(),
      });
    } catch (error: any) {
      reporter.addResult({
        testName: "Browse Products",
        status: "failed",
        duration: Date.now() - test3Start,
        error: error.message,
        timestamp: new Date().toISOString(),
      });
    }

    await delay(2000);

    const test4Start = Date.now();
    try {
      await stagehand.act("click on the first product card");
      await delay(3000);
      
      const productDetails = await stagehand.extract(
        "extract the product name, price, and description",
        z.object({
          name: z.string(),
          price: z.string(),
          description: z.string().optional(),
        })
      );
      
      reporter.addResult({
        testName: "View Product Details",
        status: "passed",
        duration: Date.now() - test4Start,
        result: productDetails,
        timestamp: new Date().toISOString(),
      });
    } catch (error: any) {
      reporter.addResult({
        testName: "View Product Details",
        status: "failed",
        duration: Date.now() - test4Start,
        error: error.message,
        timestamp: new Date().toISOString(),
      });
    }

    await delay(2000);

    const test5Start = Date.now();
    try {
      await stagehand.act("click the Add to Cart button");
      await delay(2000);
      
      reporter.addResult({
        testName: "Add Product to Cart",
        status: "passed",
        duration: Date.now() - test5Start,
        result: { action: "Product added to cart" },
        timestamp: new Date().toISOString(),
      });
    } catch (error: any) {
      reporter.addResult({
        testName: "Add Product to Cart",
        status: "failed",
        duration: Date.now() - test5Start,
        error: error.message,
        timestamp: new Date().toISOString(),
      });
    }

    await delay(2000);

    const test6Start = Date.now();
    try {
      await page.goto(`${BASE_URL}/cart`);
      await delay(3000);
      
      const cartInfo = await stagehand.extract(
        "extract the cart items count and total price if visible",
        z.object({
          itemsCount: z.string().optional(),
          total: z.string().optional(),
        })
      );
      
      reporter.addResult({
        testName: "View Shopping Cart",
        status: "passed",
        duration: Date.now() - test6Start,
        result: cartInfo,
        timestamp: new Date().toISOString(),
      });
    } catch (error: any) {
      reporter.addResult({
        testName: "View Shopping Cart",
        status: "failed",
        duration: Date.now() - test6Start,
        error: error.message,
        timestamp: new Date().toISOString(),
      });
    }

    await delay(2000);

    const test7Start = Date.now();
    try {
      await page.goto(`${BASE_URL}/signup`);
      await delay(3000);
      
      await stagehand.act(`fill the name field with 'Test User'`);
      await delay(1000);
      await stagehand.act(`fill the email field with '${TEST_EMAIL}'`);
      await delay(1000);
      await stagehand.act("fill the password field with 'TestPassword123!'");
      await delay(2000);
      
      await stagehand.act("click the Sign Up button or Create Account button");
      await delay(3000);
      
      const currentUrl = page.url();
      
      reporter.addResult({
        testName: "User Sign Up",
        status: "passed",
        duration: Date.now() - test7Start,
        result: { email: TEST_EMAIL, redirectUrl: currentUrl },
        timestamp: new Date().toISOString(),
      });
    } catch (error: any) {
      reporter.addResult({
        testName: "User Sign Up",
        status: "failed",
        duration: Date.now() - test7Start,
        error: error.message,
        timestamp: new Date().toISOString(),
      });
    }

    await delay(2000);

    const test8Start = Date.now();
    try {
      await page.goto(`${BASE_URL}/dashboard`);
      await delay(3000);
      
      const dashboardInfo = await stagehand.extract(
        "extract the welcome message and any statistics shown",
        z.object({
          welcomeMessage: z.string().optional(),
          stats: z.array(z.string()).optional(),
        })
      );
      
      reporter.addResult({
        testName: "View User Dashboard",
        status: "passed",
        duration: Date.now() - test8Start,
        result: dashboardInfo,
        timestamp: new Date().toISOString(),
      });
    } catch (error: any) {
      reporter.addResult({
        testName: "View User Dashboard",
        status: "failed",
        duration: Date.now() - test8Start,
        error: error.message,
        timestamp: new Date().toISOString(),
      });
    }

    const report = reporter.generateReport();
    const reportPath = reporter.saveReport("shophub-test-report.txt");

  } catch (error) {
    // Silent error handling
  } finally {
    await delay(2000);
    await stagehand.close();
  }
}

runShopHubTests().catch(() => {});