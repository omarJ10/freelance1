<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class DashboardInstagramController extends AbstractController
{
    #[Route('/dashboard/instagram', name: 'app_dashboard_instagram')]
    public function index(): Response
    {
        $user = $this->getUser();

        return $this->render('dashboard_instagram/index.html.twig', [
            'username' => $user->getUsername()
        ]);
    }
}
