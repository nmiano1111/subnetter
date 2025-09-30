package cmd

import (
	"fmt"

	"subnetter/internal/client"

	"github.com/spf13/cobra"
)

var (
	seedTenant string
	seedVRF    string
	seedRD     string
	seedCIDR   string
	seedStatus string
	seedMask   int
	seedCount  int
)

var seedCmd = &cobra.Command{
	Use:   "seed",
	Short: "Create a tenant, VRF, prefix, carve children, and allocate an IP",
	RunE: func(cmd *cobra.Command, args []string) error {
		cl := client.New(baseURL, idemKey)

		t, err := cl.CreateTenant(seedTenant)
		if err != nil {
			return fmt.Errorf("create tenant: %w", err)
		}
		fmt.Printf("Tenant: %s  id=%s\n", t.Name, t.ID)

		var rdPtr *string
		if seedRD != "" {
			rdPtr = &seedRD
		}
		v, err := cl.CreateVRF(t.ID, seedVRF, rdPtr)
		if err != nil {
			return fmt.Errorf("create vrf: %w", err)
		}
		fmt.Printf("VRF: %s  id=%s  rd=%v\n", v.Name, v.ID, v.RD)

		p, err := cl.CreatePrefix(v.ID, seedCIDR, seedStatus, "seed root")
		if err != nil {
			return fmt.Errorf("create prefix: %w", err)
		}
		fmt.Printf("Prefix: %s  id=%s\n", p.CIDR, p.ID)

		kids, err := cl.CarveChildren(p.ID, seedMask, seedCount)
		if err != nil {
			return fmt.Errorf("carve children: %w", err)
		}
		fmt.Printf("Carved %d children\n", len(kids))

		target := p.ID
		if len(kids) > 0 {
			target = kids[0].ID
		}
		ip, err := cl.NextIP(target)
		if err != nil {
			return fmt.Errorf("next ip: %w", err)
		}
		fmt.Printf("Allocated IP %s in prefix=%s\n", ip.Address, target)

		return nil
	},
}

func init() {
	rootCmd.AddCommand(seedCmd)
	seedCmd.Flags().StringVar(&seedTenant, "tenant-name", "DemoTenant", "tenant name")
	seedCmd.Flags().StringVar(&seedVRF, "vrf-name", "demo-vrf", "vrf name")
	seedCmd.Flags().StringVar(&seedRD, "rd", "65000:1", "route distinguisher (optional)")
	seedCmd.Flags().StringVar(&seedCIDR, "cidr", "10.0.0.0/24", "CIDR to create")
	seedCmd.Flags().StringVar(&seedStatus, "status", "active", "container|active|reserved")
	seedCmd.Flags().IntVar(&seedMask, "mask", 28, "child prefix length")
	seedCmd.Flags().IntVar(&seedCount, "count", 2, "number of child prefixes")
}
