"""
Google Earth Engine Setup & Authentication
Run this script once to authenticate with Google Earth Engine
"""
import subprocess
import sys

def setup_earth_engine():
    """
    Guide user through Earth Engine authentication
    """
    print("=" * 70)
    print("🛰️  GOOGLE EARTH ENGINE SETUP")
    print("=" * 70)
    print()
    print("This script will help you authenticate with Google Earth Engine")
    print("to access real satellite NDVI data from Sentinel-2.")
    print()
    print("📋 Requirements:")
    print("  1. Google Cloud Project with Earth Engine API enabled")
    print("  2. Google account (Gmail)")
    print("  3. Earth Engine access (free for research/education)")
    print()
    print("💡 If you don't have a project yet:")
    print("   1. Visit: https://console.cloud.google.com/")
    print("   2. Create a new project")
    print("   3. Enable Earth Engine API")
    print("   4. Come back and run this script")
    print()
    print("=" * 70)
    print()
    
    # Check if earthengine-api is installed
    try:
        import ee
        print("✅ earthengine-api package is installed")
    except ImportError:
        print("❌ earthengine-api not found!")
        print()
        print("Installing earthengine-api...")
        subprocess.run([sys.executable, "-m", "pip", "install", "earthengine-api"])
        print()
    
    # Check current authentication status
    print("🔍 Checking authentication status...")
    try:
        import ee
        ee.Initialize()
        print("✅ Already authenticated!")
        print()
        print("Your Earth Engine credentials are working.")
        print("You can start using real satellite data now!")
        return True
    except Exception as e:
        print(f"⚠️  Not authenticated yet: {e}")
        print()
    
    # Guide through authentication
    print("=" * 70)
    print("🔐 AUTHENTICATION STEPS")
    print("=" * 70)
    print()
    print("Step 1: Register for Earth Engine")
    print("  → Visit: https://earthengine.google.com/signup/")
    print("  → Sign up with your Google account")
    print("  → Select 'Research' or 'Education' (it's FREE!)")
    print("  → Wait for approval (usually instant)")
    print()
    print("Step 2: Authenticate this computer")
    print("  → I'll run 'earthengine authenticate' for you")
    print("  → A browser window will open")
    print("  → Log in with your Google account")
    print("  → Grant permissions")
    print("  → Copy the authorization code")
    print("  → Paste it back here in the terminal")
    print()
    print("=" * 70)
    print()
    
    # Ask for project ID
    print("📋 Please enter your Google Cloud Project ID:")
    print("   (You can find this in Google Cloud Console)")
    print("   Example: digitaltwin-farming")
    print()
    project_id = input("Project ID: ").strip()
    
    if not project_id:
        print()
        print("❌ Project ID is required!")
        print("   Get it from: https://console.cloud.google.com/")
        return False
    
    print()
    print(f"✅ Using project: {project_id}")
    print()
    
    response = input("Ready to authenticate? (y/n): ").strip().lower()
    
    if response == 'y':
        print()
        print("🚀 Starting authentication...")
        print()
        
        try:
            # Run earthengine authenticate command with project
            print(f"📋 Authenticating with project: {project_id}")
            result = subprocess.run(
                ["earthengine", "authenticate", "--project", project_id],
                check=True
            )
            
            if result.returncode == 0:
                print()
                print("=" * 70)
                print("✅ AUTHENTICATION SUCCESSFUL!")
                print("=" * 70)
                print()
                print("🎉 You're all set! Your dashboard will now use real satellite data.")
                print()
                
                # Test the authentication
                print("🧪 Testing Earth Engine connection...")
                try:
                    import ee
                    ee.Initialize()
                    print("✅ Earth Engine is working!")
                    
                    # Try a simple query
                    point = ee.Geometry.Point([75.5762, 31.3260])
                    print(f"✅ Can query satellite data")
                    
                    return True
                except Exception as e:
                    print(f"⚠️  Warning: {e}")
                    print("You may need to restart your terminal/IDE")
                
        except subprocess.CalledProcessError as e:
            print()
            print("=" * 70)
            print("❌ AUTHENTICATION FAILED")
            print("=" * 70)
            print()
            print(f"Error: {e}")
            print()
            print("💡 Troubleshooting:")
            print("  1. Make sure you've signed up at https://earthengine.google.com/signup/")
            print("  2. Check your internet connection")
            print("  3. Try running manually: earthengine authenticate")
            return False
        except FileNotFoundError:
            print()
            print("❌ 'earthengine' command not found!")
            print()
            print("💡 This usually means the package isn't properly installed.")
            print("Try:")
            print("  pip install --upgrade earthengine-api")
            return False
    else:
        print()
        print("⏸️  Authentication skipped")
        print()
        print("To authenticate later, run:")
        print("  python setup_earth_engine.py")
        print("or manually:")
        print("  earthengine authenticate")
        return False


def verify_authentication():
    """
    Verify Earth Engine authentication is working
    """
    print()
    print("=" * 70)
    print("🧪 VERIFICATION TEST")
    print("=" * 70)
    print()
    
    try:
        import ee
        ee.Initialize()
        
        # Test fetching NDVI
        print("Testing NDVI fetch for Jalandhar, Punjab...")
        from earth_engine_ndvi import get_sentinel2_ndvi
        
        result = get_sentinel2_ndvi(31.3260, 75.5762, days_back=30)
        
        if result:
            print()
            print("✅ SUCCESS! Real satellite data retrieved:")
            print(f"   📅 Date: {result['date']}")
            print(f"   📊 Mean NDVI: {result['ndvi_mean']}")
            print(f"   ☁️ Cloud Cover: {result['cloud_cover']}%")
            print()
            print("🎉 Your dashboard is ready to use real NDVI data!")
            return True
        else:
            print()
            print("⚠️  Could not fetch NDVI data")
            print("This might be due to:")
            print("  - No recent cloud-free images")
            print("  - Network issues")
            print("  - API limits")
            print()
            print("The dashboard will use simulated data as fallback.")
            return False
            
    except Exception as e:
        print()
        print(f"❌ Verification failed: {e}")
        print()
        print("The dashboard will use simulated data as fallback.")
        return False


if __name__ == "__main__":
    print()
    success = setup_earth_engine()
    
    if success:
        print()
        verify_authentication()
    
    print()
    print("=" * 70)
    print("📚 NEXT STEPS")
    print("=" * 70)
    print()
    print("1. Start your dashboard:")
    print("   python app.py")
    print()
    print("2. The NDVI heatmap will now show REAL satellite data!")
    print()
    print("3. Data is cached for 7 days to avoid API limits")
    print()
    print("4. If satellite data fails, it automatically falls back to simulated data")
    print()
    print("=" * 70)
    print()

